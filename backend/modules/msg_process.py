import json
import traceback
import modules.serial_canopen as serial_can
from . import ulog
from .serial_canopen import SerialCan

serial_obj = None
global_client_fd = None
END_SIGN = '|END' #  TCP结束符 处理粘包问题

# ------------------- 消息处理方法 ------------------------------------
def tcp_send(send_fd:object, json:str):
    send_fd.write((json+END_SIGN).encode('utf8'))

def msg_hello_process(send_fd:object):
    '''hello message'''
    tcp_send(send_fd, json.dumps({'msg':'hello res'}))
    ulog.debug(f'[server]: py -> js: "msg":"hello res"')

def msg_fresh_port_process(send_fd:object):
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
    send = {'msg': 'can frame', 'frame':' '.join(hex(x) for x in msg.data), 'canid':msg.arbitration_id, 'time':msg.timestamp}
    tcp_send(global_client_fd, json.dumps(send))

def msg_port_open_process(send_fd:object, com:str):
    '''端口打开处理'''
    global serial_obj
    global global_client_fd
    if serial_obj != None:
        serial_obj.close()      # 关闭
        del serial_obj          # 删除对象

    global_client_fd = send_fd
    serial_obj = SerialCan()
    serial_obj.set_recv_cb(serial_recv_cb)  # 设置信息接收回调
    serial_obj.set_err_cb(serial_err_cb)     # 设置一个异常回调，发消息回去通知
    serial_obj.open(com)
    send = {'msg':'req port open res'}
    send['result'] = serial_obj.get_connect_state()
    send['code'] = serial_obj.get_open_err_desribe() # 错误描述
    tcp_send(send_fd, json.dumps(send))
    ulog.debug(f'[server]: py -> js: {send}')

def msg_port_close_process(send_fd:object):
    '''端口关闭处理'''
    global serial_obj
    if serial_obj != None:
        serial_obj.close()      # 关闭

def msg_canopen_add_node(send_fd:object, id: int, path: str):
    '''canopen 节点添加'''
    global serial_obj
    if serial_obj == None or not serial_obj.get_connect_state():
        send = {'msg':'canopen add node res'}
        send['result'] = False
        send['id'] = id
        send['describe'] = 'can 已断开'
        tcp_send(send_fd, json.dumps(send))
        return
    result = serial_obj.add_canopen_node(id, path)
    send = {'msg':'canopen add node res'}
    send['result'] = result
    send['id'] = id
    tcp_send(send_fd, json.dumps(send))
    ulog.debug(f'[server]: py -> js: {send}')

def msg_canopen_remove_node(send_fd:object, id: int):
    '''canopen 节点移除'''
    global serial_obj
    if serial_obj == None or not serial_obj.get_connect_state():
        send = {'msg':'canopen add node res'}
        send['result'] = False
        send['id'] = id
        send['describe'] = 'can 已断开'
        tcp_send(send_fd, json.dumps(send))
        return

    result = serial_obj.remove_canopen_node(id)
    send = {'msg':'canopen remove node res'}
    send['result'] = result
    send['id'] = id
    tcp_send(send_fd, json.dumps(send))
    ulog.debug(f'[server]: py -> js: {send}')

    #  关闭串口不需要应答
# -----------------------------------------------------------------


# --------------------------- js -> py 消息回调------------------------------
def tcp_msg_process_cb(rv:str, send_fd:object):
    '''
        send_fd.write( bytes )
    '''
    print(rv)
    ulog.debug(f'[server]: js -> py: {rv}')
    
    recv_list = rv.split(END_SIGN) # TCP分包
    for recv in recv_list:
        if recv == '':
            continue

        try:
            recv_dict = json.loads(recv)

            if recv_dict['msg'] == 'hello':
                msg_hello_process(send_fd)

            # 端口刷新
            elif recv_dict['msg'] == 'fresh port':
                msg_fresh_port_process(send_fd)
                
            # 打开端口连接
            elif recv_dict['msg'] == 'req port open':
                msg_port_open_process(send_fd, recv_dict['port'])

            # 关闭端口
            elif recv_dict['msg'] == 'req port close':
                msg_port_close_process(send_fd)

            # 添加can节点
            elif recv_dict['msg'] == 'canopen add node':
                msg_canopen_add_node(send_fd, recv_dict['node'], recv_dict['eds'])
        
            # 删除canopen节点
            elif recv_dict['msg'] == 'canopen remove node':
                msg_canopen_remove_node(send_fd, recv_dict['node'])
        
        except Exception as e:
            ulog.error(traceback.format_exc())
            tcp_send(send_fd, recv)
