import os
import threading
import queue
import time
import datetime
import logging
from logging.handlers import RotatingFileHandler

SP = '‖'  # 分隔符, 尽量避免和数据冲突


class ULOG(threading.Thread):
    AQueue = queue.Queue(100000)
    nPID = os.getpid()
    Adt = datetime.datetime.now().strftime('%Y%m%d')
    nCount = 1

    def __init__(self, threadID, name, module, logLevel):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.module = module

        try:
            os.makedirs('./log')
        except:
            pass
        print("set loglevel: [%s]" % (logLevel))
        formatter = logging.Formatter(f'%(asctime)s{SP}%(name)s{SP}%(process)d{SP}%(levelname)s{SP}%(message)s')
        # logfile = "log_" + self.module + "_" + str(logging2.nPID) + "_" + str(logging2.Adt) + ".log"
        logfile = "log/log_" + self.module + "_" + str(ULOG.Adt) + ".log"
        self.logger = logging.getLogger(__name__)

        self.rHandler = RotatingFileHandler(logfile, maxBytes=10 * 1024 * 1024, backupCount=10, encoding='utf-8')
        self.rHandler.setFormatter(formatter)

        self.console = logging.StreamHandler()
        self.console.setFormatter(formatter)

        if logLevel == 'DEBUG':
            self.logger.setLevel(level=logging.DEBUG)
            self.rHandler.setLevel(logging.DEBUG)
            self.console.setLevel(logging.DEBUG)
        elif logLevel == 'INFO':
            self.logger.setLevel(level=logging.INFO)
            self.rHandler.setLevel(logging.INFO)
            self.console.setLevel(logging.INFO)
        elif logLevel == 'WARNING':
            self.logger.setLevel(level=logging.WARN)
            self.rHandler.setLevel(logging.WARN)
            self.console.setLevel(logging.WARN)
        elif logLevel == 'ERROR':
            self.logger.setLevel(level=logging.ERROR)
            self.rHandler.setLevel(logging.ERROR)
            self.console.setLevel(logging.ERROR)

        self.logger.addHandler(self.rHandler)
        self.logger.addHandler(self.console)

        # 如果跨天了，则重新生成新的文件名

    def reSetLog(self):
        AdtTemp = datetime.datetime.now().strftime('%Y%m%d')
        # 比较新的时间
        if AdtTemp == ULOG.Adt:
            return (True)

        ULOG.Adt = AdtTemp
        logfile = "log_" + self.module + "_" + str(ULOG.nPID) + "_" + str(AdtTemp) + ".log"
        self.rHandler = RotatingFileHandler(logfile, maxBytes=1 * 1024, backupCount=10)

        self.logger.addHandler(self.rHandler)
        self.logger.addHandler(self.console)
        ULOG.nCount += 1

    def run(self):
        print("开启日志线程：" + self.name)

        while True:
            # 从队列获取日志消息
            data = ULOG.AQueue.get()
            if type(data) == type("") and data == "EXIT":
                print('logging exit')
                break

            self.reSetLog()
            # 解析日志消息，格式：日志级别，内容
            print(data)
            level = list(data.keys())[0]
            content = data.get(level)
            # 把内容按分隔符{SP}解析成list传入参数
            lstContent = list(content.split(SP))
            if level == 'DEBUG':
                self.logger.debug(*lstContent)
            elif level == 'INFO':
                self.logger.info(*lstContent)
            elif level == 'WARNING':
                self.logger.warn(*lstContent)
            elif level == 'ERROR':
                self.logger.error(*lstContent)

        print("退出线程：" + self.name)


def debug(*content):
    logMsg = ""
    # 传入多个参数用竖线分隔符分开
    for i in range(len(content)):
        if i == len(content) - 1:
            logMsg += content[i]
        else:
            logMsg += content[i] + SP
    ULOG.AQueue.put({'DEBUG': logMsg})


def info(*content):
    logMsg = ""
    for i in range(len(content)):
        if i == len(content) - 1:
            logMsg += content[i]
        else:
            logMsg += content[i] + SP
    ULOG.AQueue.put({'INFO': logMsg})


def warn(*content):
    logMsg = ""
    for i in range(len(content)):
        if i == len(content) - 1:
            logMsg += content[i]
        else:
            logMsg += content[i] + SP
    ULOG.AQueue.put({'WARNING': logMsg})


def error(*content):
    logMsg = ""
    for i in range(len(content)):
        if i == len(content) - 1:
            logMsg += content[i]
        else:
            logMsg += content[i] + SP
    ULOG.AQueue.put({'ERROR': logMsg})


def exit():
    print('log req exit')
    ULOG.AQueue.put('EXIT')


def init(module, level):
    # 创建新线程
    thread1 = ULOG(1, "Thread-log", module, level)
    # 开启新线程
    thread1.start()
#    thread1.join()