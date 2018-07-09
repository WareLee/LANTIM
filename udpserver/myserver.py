#!usr/bin/env
# -*-encoding:utf-8-*-
# 求解问题：
#       问题说明： 接收来自客户端的2类消息：第一次自报家门消息,其后任何广播的消息(发到公共聊天室)
#       异常：
# 编写PDL：
#       抽象PDL: 判断消息类型。 自报家门-->新建定向子进程,然后定向子进程负责后续通信；广播-->传递数据到广播进程。
#       具体PDL：
#           数据规范：
#               客户端上报且经过server父进程去重后的username将作为server识别客户端的标识,以及视图层展示时区分用户的标识。username的命名
#               一般采用humannic的语言,server将检查重复情况,将后继重复者的username加上诸如(1)(2)这样的后缀加以区分。
#               自报家门数据格式： self:{username}:{any info}
#               请求广播格式：broadcast:{username}:{info wanted to send}, 注：广播消息根据实际到达client的时间排序
#               单播数据报格式： {time of client msg creating}:{friendusername}:{info wanted to send},注：单播消息的数据顺序由接收客户端负责
#               server针对客户端自曝家门回应的报文： server:{checkedusername}:{any info}
#               server组装单播消息： {time of client msg creating}:{sourcesusername}:{info from source client}
#               server组装广播消息： {sourceusername}:{info wanted to send}
#
#           server父进:
#               0.server父进程负责维护：广播消息队列bdcast_msgs_q,所有连线了的客户端的信息all_clients,
#               通向各个client的消息队列(使用Pipes)cli_cli_msgs_ps.
#               1.创建处理广播的子进程,
#               2.若是新客户端自报家门(自家门时必须提供自定义的username),更新all_clients,
#                检查username的重名的问题（若重名使用后缀(1)(2)形式重命名以区分）,创建定向子进程,传入检查过的username,并回传给client.
#               3.若是广播消息,放入广播的数据队列bdcast_msgs_q供广播处理子进程消费
#               (客户端如何接收广播？？？)
#
#           定向子进程：
#               回传server父进程关于username的确认信息,以及用于后继通信(发起单播消息)的定向子进程标识sonAddr.
#                (客户端必须确定自报家门成功,然后客户端最终确定自己的名字username,以及用于后继通讯的服务器子进程sonAddr,通过该地址完成后继通信)
#               若有单播消息到来,根据客户端发起方提供的客户端接收方username,将消息处理后放入对应接收方客户端的消息队列中。
#               (客户端接收方必须自行解析单播数据报,以区分发起通信的客户端username)
#

import socket
import multiprocessing as mp
import threading as th
import re
import time

HOST = '192.168.2.102'
PORT = 1069
BUFSIZE = 65536
cli_bdcast_port = 1069
msgType = {'self': 'self', 'broadcast': 'broadcast'}

# 所有向服务器自报家门的客户端地址{username: addr}, username:是每个自报家门者报告的名字(去重后),addr是报告者地址
all_clients = {}


def main():
    """创建广播进程,启动UDPServer,判断接受到的消息类型,并启动相应进程或传送数据给广播进程"""
    # 等待广播的消息队列,消息项是字符串,格式 {sourcename}:{info want to broadcast}
    bdcast_msgs_q = mp.Queue()
    # 客户端到客户端间会话消息管道{key, aPipes}, 每个客户端定向进程有一个Pipes; key是所定向的客户端addr
    cli_cli_msgs_ps = {}

    # 创建广播进程
    create_br_p(bdcast_msgs_q, cli_bdcast_port)

    # 启动UDPServer父进程
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST, PORT))

    # UDPServer接收来自客户端的请求
    while True:
        data, addr = s.recvfrom(BUFSIZE)
        dtype = _msg_type(data.encode('utf-8'))

        # 如果是自报家门的消息,创建定向服务进程
        if dtype == msgType['self']:
            # 客户端username去重
            uname = data.encode('utf-8').split(':')[1].strip()
            cli_name = _rename_cli(uname)
            # 纪录客户端信息
            if uname != cli_name:
                all_clients[cli_name] = addr
            # 创建定向服务进程
            di_server = mp.Process(target=create_di_p, args=(addr, cli_name, cli_cli_msgs_ps, cli_name))
            di_server.start()
            di_server.join()

        # 如果是广播,将消息放广播队列中
        # 接收的消息格式 broadcast:{username}:{info wanted to send}
        # 组装消息的格式 {sourceusername}:{info wanted to send}
        if dtype == msgType['broadcast']:
            cdata = data.decode('utf-8')
            b_msg = cdata[cdata.find(':', 2) + 1:].encode('utf-8')
            per_add = cdata[cdata.find(':') + 1:cdata.find(':', 2)].encode('utf-8')
            ali = _slice_msg(b_msg, per_add)
            for it in ali:
                bdcast_msgs_q.put(it)


def _rename_cli(name):
    if name.strip() in all_clients.keys():
        return name

    next_ind = 1
    for it in all_clients.keys():
        m = re.match(r'(.*)(\((\d*)\))$', it)
        if m:
            results = m.groups()
            if results[0].strip() == name:
                t = int(results[2]) + 1
                if t > next_ind:
                    next_ind = t

    return '{}({})'.format(name, next_ind)


def create_br_p(bdcast_msgs_q, bdcast_port):
    """创建广播进程"""
    bdcast_p = mp.Process(target=broct_task, args=(bdcast_msgs_q, bdcast_port))
    bdcast_p.start()
    bdcast_p.join()


def create_di_p(cli_addr, cli_name, cli_cli_msgs_ps, additional='directional msg'):
    """创建定向服务进程：

    Args:
        cli_addr: tuple(host,port), 定向服务进程所指向的客户端地址
        cli_name: 客户端名称
        additional: 字符串,该子进程创建后第一次响应客户端的自报家门请求时,fu带的消息
    """
    pipe = mp.Pipe()
    cli_cli_msgs_ps[cli_addr] = pipe

    # 首次回应客户端的连接请求
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(cli_addr)
    msg = 'server:{}:{}'.format(cli_name, additional).encode('utf-8')
    s.sendto(msg, cli_addr)

    # 接收客户端请求
    threcv = th.Thread(target=_recv_msg_task(), args=(s, cli_name, cli_cli_msgs_ps))
    threcv.start()
    threcv.join()

    # 响应客户端的请求
    thsend = th.Thread(target=_send_msg_task(), args=(s, cli_addr, cli_cli_msgs_ps))
    thsend.start()
    thsend.join()


def _recv_msg_task(sock, cli_name, cli_cli_msgs_ps):
    """接收并处理定向的客户端的消息"""
    while True:
        # 数据格式: {time of client msg creating}:{friendusername}:{info wanted to send}
        data, addr = sock.recvfrom(BUFSIZE)
        # 检查数据想要到达的客户端
        cdata = data.decode('utf-8')
        funame = cdata.split(':')[1]
        faddr = all_clients[funame]

        # 组装消息
        # {time of client msg creating}:{sourcesusername}:{info from source client}
        b_msg = cdata[cdata.find(':', 2) + 1:].encode('utf-8')
        per_add = [str(time.time()).encode('utf-8'), cli_name.encode('utf-8')]
        msgs = _slice_msg(b_msg, *per_add)

        # 将消息放到目标客户端的pipes队列中
        friend_pipe = cli_cli_msgs_ps[faddr][0]
        for it in msgs:
            friend_pipe.send(it)


def _send_msg_task(sock, cli_addr, cli_cli_msgs_ps):
    """响应定向客户端的消息"""
    pipe = cli_cli_msgs_ps[cli_addr][1]
    while True:
        sock.sendto(pipe.recv(), cli_addr)


def broct_task(q, prot):
    """将广播消息队列中的消息广播出去。

     Args:
         q: queue, 即将被转发消息的队列,每一项是一个str
         prot: 广播端口
     """
    brocast_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    brocast_s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while True:
        msg = q.get()
        sep_index = msg.find(':')
        cli_name = msg[0:sep_index]
        slices = _slice_msg(msg[sep_index + 1:].encode('utf-8'), cli_name.encode('utf-8'))

        for it in slices:
            brocast_s.sendto(it, ('<broadcast>', prot))


def _slice_msg(b_msg, *per_add, maxlen=1474):
    """ 将要广播的消息进行分片,避免广播数据太大而导致的广播失败.

    Args:
        b_msg: str, 要进行广播的二进制字符串消息
        per_add: str, 要在每个分片上额外添加的二进制数据,用于组合分片消息的头部
        maxlen: int, 分片之后的每个二进制消息的最大长度,其取值方法为1500-报文中udp或tcp头的大小,一般无需更改

    Returns:
        list: 广播的消息分片结果,所有数据项都是二进制的,格式 'head:msgxxx'
    """
    result = []
    tlt_add_len = 0
    head = b''
    for it in per_add:
        tlt_add_len += len(it)
        head += it

    msg_max_len = maxlen - tlt_add_len - len(per_add) * len(':'.encode('utf-8'))
    while len(b_msg) > msg_max_len:
        result.append(head + ':'.encode('utf-8') + b_msg[0:msg_max_len])
        b_msg = b_msg[msg_max_len:]

    result.append(head + ':'.encode('utf-8') + b_msg)
    return result


def _msg_type(msg):
    """判断用户请求消息的类型: 分2种
    自报家门的消息格式： self：username:xxx,
    广播的消息格式： broadcast:username:info data .

    Args:
        msg: str, 消息字符串

    Returns:
        str: 两种字符串 ‘self’ 或 ‘broadcast’
    """
    li = msg.split(':')
    if len(li) > 1 and li[0] == msgType['self']:
        return msgType['self']
    if len(li) > 1 and li[0] == msgType['broadcast']:
        return msgType['broadcast']


if __name__ == '__main__':
    main()
