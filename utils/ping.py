#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: yushuibo
@Copyright (c) 2018 yushuibo. All rights reserved.
@Licence: GPL-2
@Email: hengchen2005@gmail.com
@Create: httphandler.py
@Last Modified: 2018/4/1 20:57
@Desc: --
"""

import os
import struct
import array
import time
import socket

import IPy


class Ping(object):
    """
参数：
    timeout    -- Socket超时，默认3秒
    IPv6       -- 是否是IPv6，默认为False
"""

    def __init__(self, timeout=3, ipv6=False):
        self.timeout = timeout
        self.ipv6 = ipv6

        self.__data = struct.pack('d', time.time())  # 用于ICMP报文的负荷字节（8bit）
        self.__id = os.getpid()  # 构造ICMP报文的ID字段，无实际意义

    @property  # 属性装饰器
    def __socket(self):
        """创建ICMP Socket"""
        if not self.ipv6:
            sock = socket.socket(
                socket.AF_INET,
                socket.SOCK_RAW,
                socket.getprotobyname("icmp"))
        else:
            sock = socket.socket(
                socket.AF_INET6,
                socket.SOCK_RAW,
                socket.getprotobyname("ipv6-icmp"))
        sock.settimeout(self.timeout)
        return sock

    @property
    def __packet(self):
        """构造 ICMP 报文"""
        if not self.ipv6:
            # TYPE、CODE、CHKSUM、ID、SEQ
            header = struct.pack('bbHHh', 8, 0, 0, self.__id, 0)
        else:
            header = struct.pack('BbHHh', 128, 0, 0, self.__id, 0)

        packet = header + self.__data  # packet without checksum

        checksum = in_checksum(packet)  # make checksum

        if not self.ipv6:
            header = struct.pack('bbHHh', 8, 0, checksum, self.__id, 0)
        else:
            header = struct.pack('BbHHh', 128, 0, checksum, self.__id, 0)

        return header + self.__data  # packet *with* checksum

    def send(self, ip):
        """利用ICMP报文探测网络主机存活"""
        if is_ip(ip):
            sock = self.__socket
            try:
                sock.sendto(self.__packet, (ip, 0))
                resp = sock.recvfrom(1024)
            except socket.timeout:
                resp = ''
            return resp


def in_checksum(packet):
    """ICMP 报文效验和计算方法"""
    if len(packet) & 1:
        packet = packet + '\\0'
    words = array.array('h', packet)
    sum_ = 0
    for word in words:
        sum_ += (word & 0xffff)
    sum_ = (sum_ >> 16) + (sum_ & 0xffff)
    sum_ = sum_ + (sum_ >> 16)
    return (~sum_) & 0xffff


def is_ip(ip):
    """判断IP是否是一个合法的单播地址"""
    ip = [int(x) for x in ip.split('.') if x.isdigit()]
    if len(ip) == 4:
        if (0 < ip[0] < 223 and ip[0] != 127 and ip[1]
                < 256 and ip[2] < 256 and 0 < ip[3] < 255):
            return True
    return False


def make_ip_pool(start, end, ipv6=False):
    """生产 IP 地址池"""
    ip_ver = 6 if ipv6 else 4

    def int_ip(ip): return IPy.IP(ip).int()

    ip_pool = {
        IPy.intToIp(
            ip,
            ip_ver) for ip in range(
        int_ip(start),
        int_ip(end) +
        1)}
    return {ip for ip in ip_pool if is_ip(ip)}


if __name__ == '__main__':
    ping = Ping(6)
    ip = socket.gethostbyname('baidu.com')
    print('ip={}'.format(ip))
    resp = ping.send(ip)
    print(resp)
