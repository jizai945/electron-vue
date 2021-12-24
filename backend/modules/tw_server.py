#!/usr/bin/env python
# -*- coding:utf-8 -*-
 
from twisted.internet import protocol
from twisted.internet import reactor
from modules import ulog
import socket
import can.interfaces.serial.serial_can
 
SERVER_PORT = 9998
process_cb = None

 
class Process(protocol.Protocol):
    def connectionMade(self):
        ulog.debug(f'IP: {self.transport.getPeer().host}, port: {self.transport.getPeer().port}, connect')
 
    def connectionLost(self, reason):
        # ulog.debug('Lost client connection. Reason: %s' % reason)
        ulog.debug(f'IP: {self.transport.getPeer().host}, port: {self.transport.getPeer().port}, disconnect')


    def dataReceived(self, data:bytes):
        global process_cb
        if data:
            data_str = data.decode('utf8', 'ignore')
            ulog.debug(f'tcp recv: {data_str}')
            if data_str == 'exit':
                reactor.stop()
                return
            if process_cb:
                process_cb(data_str, self.transport)
            else:
                self.transport.write(data)
        else:
            self.transport.close()
        
def main(cb = None):
    try:
        # 使用客户端尝试关闭之前的服务端
        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client.settimeout(0.2)
        client.connect(('127.0.0.1', SERVER_PORT))
        client.send('exit'.encode())
        client.close()
    except Exception as e:
        print(e)
    try:
        global process_cb
        process_cb = cb
        ulog.init("server", "DEBUG")
        factory = protocol.ServerFactory()
        factory.protocol = Process
        reactor.listenTCP(SERVER_PORT, factory)
        reactor.run()
        
    except Exception as e:
        print(e)
    
    finally:
        ulog.exit()
 
def print_cb(s:str, send_fd:object):
    print(f'print_cb: f{s}')
    send_fd.write(s)

if __name__ == '__main__':
    main(print_cb) 