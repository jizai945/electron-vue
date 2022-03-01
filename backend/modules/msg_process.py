from cgitb import reset
import json
import traceback
import struct
import modules.serial_canopen as serial_can
from modules.sub_thread import *
from . import ulog
from .serial_canopen import SerialCan
from modules.mcupack_process import start_pack, read_toml_cfg
from modules.eds2c import EdsToC

serial_obj = None
global_client_fd = None
END_SIGN = '|END' #  TCP结束符 处理粘包问题

# ------------------- 消息处理方法 ------------------------------------
def tcp_send(send_fd:object, json:str):
    send_fd.write((json+END_SIGN).encode('utf8'))

def msg_hello_process(send_fd:object, recv:dict):
    '''hello message'''
    tcp_send(send_fd, json.dumps({'msg':'hello res'}))
    ulog.debug(f'[server]: py -> js: "msg":"hello res"')

def check_serial_state(serial_obj) -> bool:
    '''检查串口状态'''
    return False if serial_obj == None else True

def check_canopen_state(serial_obj) -> bool:
    '''检查canopen状态'''
    return False if ( serial_obj == None or not serial_obj.get_connect_state() ) else  True

def msg_fresh_port_process(send_fd:object, recv:dict):
    '''端口刷新处理'''
    port_dict = serial_can.serial_port_getlist()
    send_dict = {'msg':'fresh port res', 'port_value':[], 'port_label':[]}
    send_dict['port_value'] = port_dict['port_value']
    send_dict['port_label'] = port_dict['port_label']
    tcp_send(send_fd, json.dumps(send_dict))
    ulog.debug(f'[server]: py -> js: {send_dict}')

def serial_err_cb(err:str):
    '''can串口错误回调'''
    global global_client_fd
    send_dict = {'msg':'can err'}
    send_dict['describe'] = err
    tcp_send(global_client_fd, json.dumps(send_dict))
    # ulog.error(err)

def serial_recv_cb(msg):
    '''can接收数据回调'''
    send = {'msg': 'can frame', 'frame':' '.join((hex(x)[2:].zfill(2)) for x in msg.data), 'canid':msg.arbitration_id, 'time':msg.timestamp, 'dir':'r'}
    tcp_send(global_client_fd, json.dumps(send))

def serial_send_cb(msg):
    '''can发送数据回调'''
    send = {'msg': 'can frame', 'frame':' '.join((hex(x)[2:].zfill(2)) for x in msg.data), 'canid':msg.arbitration_id, 'time':msg.timestamp, 'dir':'s'}
    tcp_send(global_client_fd, json.dumps(send))

def msg_port_open_process(send_fd:object, recv:dict):
    '''端口打开处理'''
    global serial_obj
    global global_client_fd
    com = recv['port']
    if check_serial_state(serial_obj) != False:
        serial_obj.close()      # 关闭
        serial_obj = None        # 删除对象

    global_client_fd = send_fd
    serial_obj = SerialCan()
    serial_obj.set_recv_cb(serial_recv_cb)      # 设置信息接收回调
    serial_obj.set_err_cb(serial_err_cb)        # 设置一个异常回调，发消息回去通知
    serial_obj.set_send_cb(serial_send_cb)      # 设置can发送回调
    serial_obj.open(com)
    send = {'msg':'req port open res'}
    send['result'] = serial_obj.get_connect_state()
    send['code'] = serial_obj.get_open_err_desribe() # 错误描述
    tcp_send(send_fd, json.dumps(send))
    ulog.debug(f'[server]: py -> js: {send}')

def msg_port_close_process(send_fd:object, recv:dict):
    '''端口关闭处理'''
    global serial_obj
    if check_serial_state(serial_obj) != False:
        serial_obj.close()      # 关闭
        serial_obj = None
    #  关闭串口不需要应答

def msg_can_send_frame(send_fd:object, recv:dict):
    '''can发送一帧数据'''
    global serial_obj
    if check_serial_state(serial_obj) == False:
        send = {'msg':'can send frame res'}
        send['result'] = False
        send['code'] = 'can未打开' # 错误描述
        tcp_send(send_fd, json.dumps(send))
        ulog.debug(f'[server]: py -> js: {send}')
        return

    try:
        bt = bytes.fromhex(recv['frame'])
        offset = 0
        while offset < len(bt):
            size = 8 if offset + 8 < len(bt) else len(bt) - offset
            serial_obj.send_one_frame(recv['canID'], bt[offset: offset+size])
            offset += 8
    except Exception as e:
        # 错误才反馈
        print(e)
        send = {'msg':'can send frame res',
                'result': False,
                'code': str(e)} # 错误描述
        tcp_send(send_fd, json.dumps(send))
        ulog.debug(f'[server]: py -> js: {send}')


def msg_canopen_add_node(send_fd:object, recv:dict):
    '''canopen 节点添加'''
    global serial_obj
    id = recv['node']
    path = recv['eds']
    if check_canopen_state(serial_obj) == False:
        send = {'msg':'canopen add node res',
                'result': False,
                'id': id,
                'describe': 'can 已断开'}
        tcp_send(send_fd, json.dumps(send))
        return
    res, des = serial_obj.add_canopen_node(id, path)
    send = {'msg':'canopen add node res',
            'result': res,
            'id': id,
            'describe': des}
    tcp_send(send_fd, json.dumps(send))
    ulog.debug(f'[server]: py -> js: {send}')

def msg_canopen_remove_node(send_fd:object, recv:dict):
    '''canopen 节点移除'''
    global serial_obj
    id = recv['node']
    if check_canopen_state(serial_obj) == False:
        send = {'msg':'canopen remove node res',
                'result': False,
                'id': id,
                'describe': 'can 已断开'}
        tcp_send(send_fd, json.dumps(send))
        return

    result = serial_obj.remove_canopen_node(id)
    send = {'msg':'canopen remove node res',
            'result': result,
            'id': id}
    tcp_send(send_fd, json.dumps(send))
    ulog.debug(f'[server]: py -> js: {send}')

def msg_canopen_node_upload(send_fd: object, recv: dict):
    '''canopen 节点升级'''
    global serial_obj
    id = recv['id']
    file = recv['file']

    if check_canopen_state(serial_obj) == False:
        send = {'msg':'canopen upload start res',
                'result': False,
                'id': id,
                'describe': 'can 已断开'}
        tcp_send(send_fd, json.dumps(send))
        return
    
    # 开线程去处理
    def uplaod_run_func(*args, **kwargs):
        print('*'*30)
        id = kwargs['id']
        file = kwargs['file']
        res, des = serial_obj.start_upload_func(id, file)
        send = {'msg':'canopen upload start res',
                'result': res,
                'id': id,
                'describe': des}
        tcp_send(send_fd, json.dumps(send))
        ulog.debug(f'[server]: py -> js: {send}')

    thread_run(uplaod_run_func, id=id, file=file)
    
def msg_canopen_read_sdo(send_fd: object, recv: dict):
    '''canopen 读取sdo数据'''
    if check_canopen_state(serial_obj) == False:
        send = {'msg':'canopen read sdo res', 
                'result':False,
                'id': recv['id'],
                'idx': recv['idx'],
                'subIdx': recv['subIdx'],
                'describe': 'can 已断开'}
        tcp_send(send_fd, json.dumps(send))
        ulog.debug(f'[server]: py -> js: {send}')
        return

    id = recv['id']
    idx = int(recv['idx'], 16)
    subIdx = int(recv['subIdx'], 16) if recv['subIdx'] != '' else -1
    # 开线程去处理
    def read_sdo_func(*args, **kwargs):
        id = kwargs['id']
        idx = kwargs['idx']
        subIdx = kwargs['subIdx']
        send = {'msg':'canopen read sdo res', 
                'result':True,
                'id': recv['id'],
                'idx': recv['idx'],
                'subIdx': recv['subIdx']}
        try:
            data = serial_obj.read_sdo_by_idx(id, idx, subIdx)
            send['data'] = str(data)
            print(f'read sucess: {data}')
        except Exception as e:
            print(e)
            send['result'] = False
            send['describe'] = str(e)   
        tcp_send(send_fd, json.dumps(send))
        ulog.debug(f'[server]: py -> js: {send}')

    thread_run(read_sdo_func, id=id, idx=idx, subIdx=subIdx)

def canopen_auto_sdo_recv_cb(id:int, sdo:dict):
    '''canopen 自动sdo读取成功回调'''
    send = {'msg': 'canopen auto sdo recv res', 'id':id, 'sdo':sdo}
    tcp_send(global_client_fd, json.dumps(send))
    ulog.debug(f'[server]: py -> js: {send}')

def msg_canopen_auto_sdo(send_fd: object, recv: dict):
    '''打开/关闭 自动读取sdo数据'''
    global serial_obj
    state = recv['state']
    if check_canopen_state(serial_obj) == False:
        if  state == 'open':
            send = {'msg':'canopen auto sdo res', 
                    'result': False,
                    'state': state,
                    'id': recv['id'],
                    'describe': 'can 已断开'}
            tcp_send(send_fd, json.dumps(send))
        else:
            send = {'msg':'canopen auto sdo res', 
                    'result': True,
                    'state': state,
                    'id': recv['id'],
                    'describe': ''}
            tcp_send(send_fd, json.dumps(send))
        ulog.debug(f'[server]: py -> js: {send}')
        return

    id = recv['id']
    if state == 'open':
        serial_obj.set_auto_sdo_recv_cb(canopen_auto_sdo_recv_cb)
        result, describe = serial_obj.open_auto_read_sdo_by_id(id)
    else:
        result, describe = serial_obj.close_auto_read_sdo_by_id(id)

    send = {'msg':'canopen auto sdo res', 
                    'result':result,
                    'state': state,
                    'id': recv['id'],
                    'describe': describe}
    tcp_send(send_fd, json.dumps(send))
    ulog.debug(f'[server]: py -> js: {send}')

def msg_canopen_sdo_change(send_fd: object, recv: dict): 
    '''sdo写'''
    
    global serial_obj
    if check_canopen_state(serial_obj) == False:
        send = {'msg':'canopen sdo data change res', 
                'result':False,
                'id': recv['id'],
                'idx': recv['idx'],
                'subIdx': recv['subIdx'],
                'describe': 'can 已断开'}
        tcp_send(send_fd, json.dumps(send))
        ulog.debug(f'[server]: py -> js: {send}')
        return

    id = recv['id']
    idx = int(recv['idx'], 16)
    subIdx = int(recv['subIdx'], 16) if recv['subIdx'] != '' else -1
    data = recv['data']
    type = recv['type']
    # 开线程去处理
    def read_sdo_func(*args, **kwargs):
        send = {'msg':'canopen sdo data change res', 
                'result':True,
                'id': recv['id'],
                'idx': recv['idx'],
                'subIdx': recv['subIdx']}
                
        id = kwargs['id']
        idx = kwargs['idx']
        subIdx = kwargs['subIdx']
        type = kwargs['type']
        try:
            data = kwargs['data']
            if type == 'int':
                # data = struct.pack('<L', int(data))
                data = int(data)
            else:
                data = data.encode('ascii')
            serial_obj.write_sdo_by_idx(data, id, idx, subIdx)
        except Exception as e:
            print(e)
            send['result'] = False
            send['describe'] = str(e)   
        tcp_send(send_fd, json.dumps(send))
        ulog.debug(f'[server]: py -> js: {send}')

    thread_run(read_sdo_func, id=id, idx=idx, subIdx=subIdx, data=data, type=type)

def msg_read_pack_toml_cfg(send_fd: object, recv: dict):
    '''读取分区表配置'''
    send = {'msg':'read pack toml cfg res', 
                'result':True,
                'data': {},
                'describe': ''}
    try:
        ret = read_toml_cfg()
        send['data'] = ret
    except Exception as e:
        send['result'] = False
        send['describe'] = str(e)
    
    tcp_send(send_fd, json.dumps(send))
    ulog.debug(f'[server]: py -> js: {send}')


def msg_pack_mcu_file(send_fd: object, recv: dict):
    '''打包'''
    send = {'msg':'pack res', 
                'result':True,
                'describe': ''}
    try:
        ret = start_pack(recv)
    except Exception as e:
        ret = False
        send['describe'] = str(e)
    send['result'] = ret
    
    tcp_send(send_fd, json.dumps(send))
    ulog.debug(f'[server]: py -> js: {send}')

def msg_eds_convert(send_fd: object, recv: dict):
    '''eds转换工具'''
    send = {'msg':'eds convert res', 
                'result':True,
                'describe': ''}
    
    e = EdsToC(recv['data']['eds'], recv['data']['runtime'], recv['data']['user'])
    send['result'] = e.start_convert()
    send['describe'] = e.get_err()

    tcp_send(send_fd, json.dumps(send))
    ulog.debug(f'[server]: py -> js: {send}')

# -----------------------------------------------------------------


# --------------------------- js -> py 消息回调------------------------------
# 字典匹配比if else效率高
js2pyMsgCb = {
    'hello':msg_hello_process,                          # hello for test
    'fresh port': msg_fresh_port_process,               # 端口刷新
    'req port open': msg_port_open_process,             # 打开端口连接
    'req port close': msg_port_close_process,           # 关闭端口
    'can send frame': msg_can_send_frame,               # can发送一帧 
    'canopen add node': msg_canopen_add_node,           # 添加can节点
    'canopen remove node': msg_canopen_remove_node,     # 删除canopen节点
    'canopen upload start': msg_canopen_node_upload,    # canopen节点升级 
    'canopen read sdo': msg_canopen_read_sdo,           # 通过sdo读取数据
    'canopen auto sdo': msg_canopen_auto_sdo,           # 自动读取sdo 打开/关闭
    'canopen sdo data change': msg_canopen_sdo_change,  # 通过sdo修改数据
    'read pack toml cfg':msg_read_pack_toml_cfg,        # 读取分区表配置
    'start pack': msg_pack_mcu_file,                    # 打包mcu文件
    'eds convert': msg_eds_convert,                     # eds 转换消息
}

def tcp_msg_process_cb(rv:str, send_fd:object):
    '''
        send_fd.write( bytes )
    '''

    global js2pyMsgCb
    print(rv)
    ulog.debug(f'[server]: js -> py: {rv}')
    
    recv_list = rv.split(END_SIGN) # TCP分包
    for recv in recv_list:
        if recv == '':
            continue

        try:
            recv_dict = json.loads(recv)

            if recv_dict['msg'] in js2pyMsgCb:
                js2pyMsgCb[recv_dict['msg']](send_fd, recv_dict)
            else:
                ulog.debug('msg unknown')

        except Exception as e:
            ulog.error(traceback.format_exc())
            tcp_send(send_fd, recv)
