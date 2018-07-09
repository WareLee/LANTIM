# 请求服务器转发消息到对应好友的客户端,
# 从服务器接收消息
# 数据的解析和组装由前端显示层view负责
import socket
import threading as th
from queue import Queue


class Requests(object):
    parent_addr = ('', 1096)  # 服务器父进程addr
    child_addr = ('', 1096)  # 服务器定向子进程addr

    def __init__(self, username, host, port=1096, br_port=1097):
        self.host = host
        self.host = port
        self.br_port = br_port
        self.username = username.strip()
        # 向定向服务进程发送或接收数据
        self.f2f_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        # 仅用于接收广播消息,和请求服务器转发广播消息
        self.br_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.br_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.br_sock.bind(('', self.br_port))
        # 存放将要广播的消息的队列
        self.send_br_queue = Queue()
        # 接收的广播的消息的队列
        self.recv_br_queue = Queue()
        # 接收来自定向服务器的消息
        self.recv_f2f_queue = Queue()
        # 存放将要发送给定向服务器的消息
        self.send_f2f_queue = Queue()

    # self:{username}:{any info}
    # 回应的报文： server:{checkedusername}:{any info}
    def _report(self, additional=''):
        """客户端自报家门"""
        # 自报家门
        msg = 'self:{}:{}'.format(self.username, additional).encode('utf-8')
        data, actualserver = self.sock.sendto(msg, Requests.parent_addr)
        # 更新服务器定向子进程
        Requests.child_addr = actualserver
        self.f2f_sock.connect(Requests.child_addr)
        # 更新本客户端的用户名
        self.username = data.decode('utf-8').split(':')[1]

    def _recv_f2f_task(self):
        while True:
            data, addr = self.f2f_sock.recvfrom(1500)
            info = self.recv_f2f_queue.put(data.decode('utf-8'))

    def _send_f2f_task(self):
        """请求服务器转发消息给朋友"""
        while True:
            info = self.send_f2f_queue.get()
            self.f2f_sock.send(info.encode('utf-8'))

    def _send_gchat_task(self):
        """发送群聊消息"""
        while True:
            info = self.send_br_queue.get()
            self.br_sock.sendto(info.encode('utf-8'), ('<broadcast>', self.br_port))

    def _recv_gchat_task(self):
        """接收广播消息"""
        while True:
            data, addr = self.br_sock.recvfrom(1500)
            self.recv_br_queue.put(data.decode('utf-8'))

    def startup(self):
        """启动业务逻辑"""

        # 自报家门
        self._report()

        # 启动客户端的业务进程
        th1 = th.Thread(target=self._recv_f2f_task)
        th2 = th.Thread(target=self._send_f2f_task)
        th3 = th.Thread(target=self._send_gchat_task)
        th4 = th.Thread(target=self._recv_gchat_task)
        th1.start()
        th2.start()
        th3.start()
        th4.start()

    def send_br(self, info):
        """将要发送的广播消息放入队列"""
        self.send_br_queue.put(info)

    def send_f2f(self, info):
        """将要请求转发的消息放入队列"""
        self.send_f2f_queue(info)

    def get_br(self):
        """获取广播消息队列"""
        return self.recv_br_queue

    def get_f2f(self):
        """获取来自好友的消息"""
        return self.recv_f2f_queue
