import types
from typing import Tuple
import canopen
import time
import serial, serial.tools.list_ports
import struct
import traceback
try:
    from modules.sub_thread import *
    from modules.crc32 import *
    from modules import ulog
except:
    from sub_thread import *
    from crc32 import *
    import ulog
from can import Message

HEAD = 'PUDUMCUFILE'
file_info_json_len = 1*1024     # 文件描述信息json字符串长度
json_str_end = '‖'              # json字符串结束符

def listen_cb(msg):
    print(f'lcb: {msg}')

def my_serial_send(self, msg, timeout=None):
    '''Reconstruction sending method'''

    try:
        a_id = struct.pack('>I', msg.arbitration_id)
        # print(f'my_serial_send id: {a_id}')
    except struct.error:
        raise ValueError('Arbitration Id is out of range')
    send_array = bytearray([0x57, 0x58])                            # USB数据头
    send_array += bytearray(a_id[2:4])                              # can id
    send_array += bytearray(msg.data[:msg.dlc])                     # can数据
    send_array += bytearray([0 for _ in range(8 - msg.dlc)])        # 补零
    send_array += bytearray([msg.dlc])                              # 实际数据长度
    send_array += bytearray([0xA8, 0XA7])                           # USB数据尾
    self.ser.write(bytearray(send_array))                           # 发送
    
    print('send:', " ".join([hex(int(i)) for i in send_array]))   # debug 打印


def my_recv_internal(self, timeout):
    '''Reconstruction receiving method'''

    rx_byte = self.ser.read()
    if rx_byte and ord(rx_byte) == 0x57:
        rx_byte = self.ser.read()
        if not (rx_byte and ord(rx_byte) == 0x58):
            return None, False
        s = bytearray([0, 0, 0, 0])
        t = bytearray(self.ser.read(2))
        s[1], s[0] = t[0], t[1]
        arb_id = (struct.unpack('<I', s))[0]

        data = self.ser.read(8)
        dlc = ord(self.ser.read())
        rxd_byte = self.ser.read(2)
        timestamp = time.time()
        if rxd_byte and rxd_byte[0] == 0xA8 and rxd_byte[1] == 0xA7:
            # received message data okay
            msg = Message(timestamp=timestamp,
                            arbitration_id=arb_id,
                            dlc=8,
                            data=data)
            return msg, False

    else:
        return None, False


def on_emcy(self, can_id, data, timestamp):
        code, register, data = EMCY_STRUCT.unpack(data)
        entry = EmcyError(code, register, data, timestamp)

        with self.emcy_received:
            if code & 0xFF00 == 0:
                # Error reset
                self.active = []
            else:
                self.active.append(entry)
            self.log.append(entry)
            self.emcy_received.notify_all()

        for callback in self.callbacks:
            callback(can_id, entry) # 把canid带上，这样知道是哪个节点回调

def serial_port_getlist() -> dict:
    '''
        获取串口端口列表
        return : {'port_value': ['COM116'], 'port_label': ['COM116 --- USB-Enhanced-SERIAL-B CH342 (COM116) pid: 55d2 vid: 1a86 ']}
    '''
    Com_Dict = {'port_value':[], 'port_label':[]}
    port_list = list(serial.tools.list_ports.comports())
    for port in port_list:
        if port.pid != None and port.vid != None:
            pid = hex(port.pid)[2:]
            vid = hex(port.vid)[2:]
        else:
            pid = 'none'
            vid = 'none'
        # 添加标识
        add_identification = ''

        if pid == '5740' and vid == '483':
            add_identification = ' (PUDU CAN)'

        Com_Dict['port_value'].append(port[0])
        Com_Dict['port_label'].append(f'{port[0]} --- {port[1]} pid: {pid} vid: {vid} {add_identification}')
    
    return Com_Dict

# can的串口类
class SerialCan():
    def __init__(self):
        self.serial_state = False # 串口状态 True连接  False断开
        self.network = canopen.Network()
        self.add_recv_cb(listen_cb)     # 设置接收数据回调，调试用
        self.err_cb = None
        self.open_err_desribe = ''   # 打开错误描述
        self.com_name = ''

    def __del__(self):
        print('serial del')

    def __check_thread_stop(self):
        try:
            thread_exit(self.check_thread)
        except:
            pass

    def __check_thread_run(self):
        self.__check_thread_stop()
        self.check_thread = thread_run(self.check_run)

    def close(self):
        '''断开串口'''
        self.__check_thread_stop()
        try:
            # self.network.bus.flushInput()
            self.network.sync.stop()
            self.network.disconnect()
            ser = serial.Serial(self.com_name, 115200) 
        except Exception as e:
            print(e)

        self.serial_state = False 

    def open(self, com:str) -> bool:
        '''打开串口'''
        # 打开异常检查线程
        self.__check_thread_run()

        self.open_err_desribe = ''
        try:
            cb = self.network.listeners[1] # 打开头1s不把数据抛出去，因为串口缓存里面有脏数据
            self.network.listeners[1] = listen_cb
            self.com_name = com
            self.network.connect(bustype="serial",  channel=com)
            self.network.bus.send = types.MethodType(my_serial_send, self.network.bus)  # 重构发送方法
            self.network.bus._recv_internal = types.MethodType(my_recv_internal, self.network.bus)  # 重构接收方法
            self.serial_state = True
            time.sleep(0.5)
            self.network.listeners[1] = cb
        except Exception as e:
            print(e)
            self.open_err_desribe = str(e)
            return False
        
        return True

    def get_open_err_desribe(self):
        '''获取打开失败错误描述'''
        return self.open_err_desribe

    def send_one_frame(self, canid:int, frame:bytes):
        '''通过串口发送一帧can数据'''
        if self.serial_state == False:
            return False
        
        self.network.send_message(canid, frame)
        return True

    def add_canopen_node(self, id:int, eds:str) -> Tuple[bool, str] :
        '''添加canopen节点'''
        try:
            node = canopen.RemoteNode(id, eds)
            self.network.add_node(node)
        except Exception as e:
            print(traceback.format_exc())
            return False, str(traceback.format_exc())
        return True, ''

    def remove_canopen_node(self, id: int) -> bool:
        '''删除一个节点'''
        try:
            del self.network.nodes[id]
        except Exception as e:
            print(traceback.format_exc())
            if self.err_cb != None:
                self.err_cb(str(e))

            return False
        return True
    
    def read_sdo_by_name(self, id, name:str) -> str:
        '''通过字典名字读取sdo数据'''
        # ！！！ 这里没有做异常捕获, 读取错误时会把异常抛出，需要外面做异常捕获
        return self.network.nodes[id][name]


    def read_sdo_by_idx(self, id, idx:int, subindx:int) -> str:
        '''通过字典索引读取sdo数据'''
        # ！！！ 这里没有做异常捕获, 读取错误时会把异常抛出，需要外面做异常捕获
        return self.network.nodes[id][idx][subindx]

    def start_upload_func(self, canid:int, file:str) -> Tuple[bool, str]:
        '''
        开始升级处理函数
        返回值:
            -> bool: True成功 False失败
            -> str: 成功为空  失败返回错误原因
        '''
        global HEAD
        global file_info_json_len
        try:
            # 判断节点的是否导入eds
            if canid not in self.network.nodes:
                print(f'canid: {canid} eds file not import')
                return (False, f'canid: {canid} eds file not import')

            # 通过判断文件头数据是否是合法的升级文件
            with open(file, 'rb') as f:
                data = f.read(len(HEAD))
            if data != HEAD.encode('utf-8'):
                return False, '不是合法的升级文件'

            node = self.network.nodes[canid]
            # 重构对象方法
            node.on_emcy = types.MethodType(on_emcy, self.network.nodes[canid])  # 重构紧急报文
            # 紧急报文回调函数
            if len(node.emcy.callbacks) == 0:
                node.emcy.add_callback(self.emcy_cb)

            # 重置状态为upload状态
            node.sdo[0x6000][2].raw = 1

            # 判断当前是否进入文件描述信息接收状态 尝试三次
            times = 3
            while times:
                times -= 1
                if node.sdo[0x6000][1].raw == 0x01:
                    break
                elif times == 0:
                    ulog.debug('node not entry info recv state')
                    return (False, 'node not entry info recv state')
                time.sleep(0.5)


            # 读取文件描述信息json字符串
            with open(file, 'rb') as f:
                f.seek(len(HEAD) + 4 + 4, 0)
                data = f.read(file_info_json_len)

            data = data.split(json_str_end.encode('utf-8'))[0]

            # 写入文件描述信息的crc32值
            node.sdo[0x6000][5].raw = crc32_bytes(data)
            ulog.debug('send info json start')
            # 写入文件
            file_size = len(data)
            file_offset = 0
            file_pack_max_size = 512
            while file_offset < file_size:
                size = file_pack_max_size if (file_offset + file_pack_max_size) < file_size else file_size - file_offset
                with node.sdo[0x6000][4].open('wb', size=size, block_transfer=True) as fp:
                    fp.write(data[file_offset:file_offset+size])
                file_offset += size

            ulog.debug('send info json sucess')

            # 判断是否有紧急报文crc32出错 和 是否不支持的文件描述的紧急报文
            # TODO
            time.sleep(0.5)

            # 判断当前状态是否文件接收状态
            times = 3
            while times:
                times -= 1
                # 判断是否退出文件接收状态
                if node.sdo[0x6000][1].raw == 0x02:
                    ulog.debug('node enter recv file state')
                    break
                elif times == 0:
                    ulog.debug('node not entry info recv state')
                    return (False, 'node not entry info recv state')
                time.sleep(0.5)

            while True:
                # 读取块数据位置
                offset = node.sdo[0x6000][6].raw
                # 块长度
                block_len = node.sdo[0x6000][7].raw
                ulog.debug(f'upload file offset: {offset} len: {block_len}')

                # 读取偏移的文件
                with open(file, 'rb') as f:
                    f.seek(offset)
                    data = f.read(block_len)

                 # 写入文件描述信息的crc32值
                node.sdo[0x6000][5].raw = crc32_bytes(data)

                # 写入文件
                with node.sdo[0x6000][4].open('wb', size=len(data), block_transfer=True) as fp:
                    fp.write(data)

                time.sleep(1)
                # 判断是否退出文件升级模式
                if node.sdo[0x6000][1].raw != 0x02:
                    ulog.debug('mcu out recv file state')
                    break

        except Exception as e:
            print(e)
            ulog.error(str(traceback.format_exc())) # 信息太长
            return (False, str(e))

        return (True, '')

    def set_err_cb(self, cb):
        '''
            设置异常出错回调
            cb(str)
        '''
        self.err_cb = cb

    def add_recv_cb(self, cb):
        '''添加数据接收回调'''
        self.network.listeners.append(cb)
    
    def set_recv_cb(self, cb):
        '''覆盖数据接收回调'''
        self.network.listeners[1] = cb

    def emcy_cb(self, canid:int, text:str):
        '''紧急报文回调函数'''
        print(f'emcy cb[id: {canid}]: {text}')

    def get_connect_state(self) -> bool:
        '''获取连接状态'''
        return self.serial_state

    def check_run(self):
        '''检查串口运行异常, 并终止串口'''
        while True:
            time.sleep(1)

            if self.serial_state:
                try:
                    self.network.check()
                except Exception as e:
                    print(traceback.format_exc())
                    if self.err_cb != None:
                        self.err_cb(str(e))
                    self.serial_state = False
                    try:
                        self.network.disconnect() # 尝试断开
                    except:
                        pass


if __name__ == '__main__':
    COM_PORT = 'COM6'

    # example 1

    # try:
    #     # Start with creating a network representing one CAN bus
    #     network = canopen.Network()

    #     # Add some nodes with corresponding Object Dictionaries
    #     node = canopen.RemoteNode(6, './eds/CANopenSocket.eds')
    #     network.add_node(node)
    #     node2 = canopen.RemoteNode(7, './eds/e35.eds')
    #     network.add_node(node2)

    #     # Add some nodes with corresponding Object Dictionaries
    #     network.connect(bustype="serial",  channel=COM_PORT)
    #     network.bus.send = types.MethodType(my_serial_send, network.bus)  # 重构发送方法
    #     network.bus._recv_internal = types.MethodType(my_recv_internal, network.bus)  # 重构接收方法

    #     network.listeners.append(listen_cb)                 # 添加一个监听回调函数

    #     # send test message
    #     network.send_message(0x06, bytes([0x11, 0x22]))

    #     # node = canopen.RemoteNode(6, './backend/eds/CANopenSocket.eds')
    #     # network.add_node(node)
    #     # node2 = canopen.RemoteNode(7, './backend/eds/e35.eds')
    #     # network.add_node(node2)

    #     print('-'*30)
    #     tick = 30
    #     while tick > 0:
    #         network.check()
    #         time.sleep(1)

    #     network.sync.stop()
    #     network.disconnect()

    # except Exception as e:
    #     print(traceback.format_exc())
    #     print('can err')

    # example 2
    # try:
    #     port_dict = serial_port_getlist()
    #     print(port_dict)

    #     serial_obj = SerialCan()   # 初始化对象
    #     serial_obj.set_err_cb(lambda str: print) # 设置异常回调
    #     serial_obj.open(COM_PORT)       # 打开com口
    #     print(serial_obj.get_connect_state())
        
    #     node = canopen.RemoteNode(7, 'C:\\Users\\Wang\\Desktop\\e35.eds')
    #     serial_obj.network.add_node(node)

    #     # print(node)
    #     # print(serial_obj.network.nodes)
    #     # print(dir(serial_obj.network.nodes[7].sdo))
    #     serial_obj.network.nodes[7].sdo.RESPONSE_TIMEOUT = 0.5      # 设置超时时间
    #     serial_obj.network.nodes[7].sdo.MAX_RETRIES = 3             # 重试次数
    #     print(serial_obj.network.nodes[7].sdo.RESPONSE_TIMEOUT) 
    #     tick = 30
    #     while tick > 0:
    #         time.sleep(1)
    #         tick -= 1

    #         try:
    #             begin_time = time.time()
    #             # device_name = node.sdo['Device name'].raw
    #             ret = node.sdo['Hardware version'].raw
    #             print(ret)
    #             print(dir(ret))
    #         except Exception as e:
    #             print(e)
    #         end_time = time.time()
    #         print ('该循环程序运行时间：', (end_time - begin_time))
    #         # vendor_id = node.sdo[0x1018][1].raw
    #         if not serial_obj.get_connect_state():
    #             print(f'serial disconnect, retry connect res: {serial_obj.open(COM_PORT)}')

    #     serial_obj.close()      # 关闭
    #     del serial_obj          # 删除对象
    #     time.sleep(1)
    # except Exception as e:
    #     print(traceback.format_exc())
    #     print('can err')

    # example 3 download file
    try:
        serial_obj = SerialCan()   # 初始化对象
        serial_obj.set_err_cb(lambda str: print) # 设置异常回调
        serial_obj.open(COM_PORT)       # 打开com口
        print(serial_obj.get_connect_state())

        # node = canopen.RemoteNode(6, 'C:\\Users\\Wang\\Desktop\\e35-pudu.eds')
        node = canopen.RemoteNode(6, './e35-pudu.eds')
        serial_obj.network.add_node(node)

        serial_obj.network.nodes[6].sdo.MAX_RETRIES = 3             # 重试次数
        serial_obj.network.nodes[6].sdo.RESPONSE_TIMEOUT = 0.3      # 设置超时时间

        serial_obj.start_upload_func(6, './test.bin')

    # example 4 upload 
    # try:
    #     serial_obj = SerialCan()   # 初始化对象
    #     serial_obj.set_err_cb(lambda str: print) # 设置异常回调
    #     serial_obj.open(COM_PORT)       # 打开com口
    #     print(serial_obj.get_connect_state())

    #     node = canopen.RemoteNode(6, 'C:\\Users\\Wang\\Desktop\\e35-pudu.eds')
    #     serial_obj.network.add_node(node)

    #     serial_obj.network.nodes[6].sdo.MAX_RETRIES = 3             # 重试次数
    #     serial_obj.network.nodes[6].sdo.RESPONSE_TIMEOUT = 0.5      # 设置超时时间

    #     map = node.pdo.tx[1]
    #     read_len = map.add_variable(0x6000, 5)   # 数据长度
    #     read_crc = map.add_variable(0x6000, 4)   # crc
    #     # map.add_variable('download parameter', 'data crc', length=4)
    #     # print(type(read_len.raw))
    #     print(map['download parameter.data len'].raw)
    #     print(map['download parameter.data crc'].raw)
    #     def emcy_cb(text):
    #         print(f'emcy_cb: {text}')
    #     node.emcy.add_callback(emcy_cb)    # 紧急报文回调

    #     # 判断是否支持升级
    #     if node.sdo[0x6000][0].raw != 7:
    #         print('node not support download')
    #         exit(1)
        
    #     # 当前状态是否支持升级
    #     if node.sdo[0x6000][1].raw != 0x01:
    #         print('state no support download')
    #         exit(1)

    #     # 发送文件名
    #     data = b'test_file_name.bin'
    #     fp = node.sdo[0x6000][3].open('wb', size=len(data), block_transfer=True)
    #     fp.write(data)
    #     fp.close()

    #     # 请求下载
    #     node.sdo[0x6000][2].raw = 1

    #     # 子索引03 写入文件描述json字符串
    #     # TODO
        
    #     # 子索引04 写入json字符串crc32值
    #     # TODO

    #     # 子索引05 写入文件描述信息json字符串长度
    #     # TODO


    #     map.stop()
    except Exception as e:
        print(traceback.format_exc())
        print('can err')