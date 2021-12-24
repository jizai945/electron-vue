import types
import canopen
import time
import serial, serial.tools.list_ports
import struct
import traceback
from .sub_thread import *
from can import Message


def listen_cb(msg):
    print(f'lcb: {msg}')

def my_serial_send(self, msg, timeout=None):
    '''Reconstruction sending method'''

    print('my_serial_send')
    try:
        a_id = struct.pack('<I', msg.arbitration_id)
    except struct.error:
        raise ValueError('Arbitration Id is out of range')
    send_array = bytearray([0x57, 0x58])                            # USB数据头
    send_array += bytearray(a_id[2:4])                              # can id
    send_array += bytearray(msg.data[:msg.dlc])                     # can数据
    send_array += bytearray([0 for _ in range(8 - msg.dlc)])        # 补零
    send_array += bytearray([msg.dlc])                              # 实际数据长度
    send_array += bytearray([0xA8, 0XA7])                           # USB数据尾
    self.ser.write(bytearray(send_array))                           # 发送


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

    def add_canopen_node(self, id:int, eds:str) -> bool:
        '''添加canopen节点'''
        try:
            node = canopen.RemoteNode(id, eds)
            self.network.add_node(node)
        except Exception as e:
            print(traceback.format_exc())
            if self.err_cb != None:
                self.err_cb(str(e))
            return False
        return True

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

    try:
        port_dict = serial_port_getlist()
        print(port_dict)

        serial_obj = SerialCan()   # 初始化对象
        serial_obj.set_err_cb(lambda str: print) # 设置异常回调
        serial_obj.open(COM_PORT)       # 打开com口
        print(serial_obj.get_connect_state())
        
        tick = 30
        while tick > 0:
            time.sleep(1)
            tick -= 1
            if not serial_obj.get_connect_state():
                print(f'serial disconnect, retry connect res: {serial_obj.open(COM_PORT)}')

        serial_obj.close()      # 关闭
        del serial_obj          # 删除对象
        time.sleep(1)
    except Exception as e:
        print(traceback.format_exc())
        print('can err')