from sys import modules
from modules import tw_server
from modules.msg_process import tcp_msg_process_cb

if __name__ == '__main__':
    tw_server.main(tcp_msg_process_cb)

