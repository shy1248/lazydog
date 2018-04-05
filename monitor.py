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

from abc import ABCMeta
from abc import abstractmethod
import threading
import time

from fuckpy.email_ import Email
from logger import logger

ALARM_STR = """\
严重告警：
    服务器不可达！

详情：
    服务器：        %(name)s
    IP地址：        %(ip)s
"""

CANCELED_ALARM = """\
告警解除！

以下是原始告警信息：
=======================================================================================
严重告警：
    服务器不可达！

详情：
    服务器：        %(name)s
    IP地址：        %(ip)s
"""


class Monitor(threading.Thread):
    __metaclass__ = ABCMeta

    def __init__(self, interval):
        threading.Thread.__init__(self)
        self.servers = []
        self.interval = interval

    @abstractmethod
    def watch(self, server):
        pass

    @staticmethod
    def send_alarm(subject, msg):
        logger.info(msg)
        email = Email(subject, msg)
        email.send()

    def run(self):
        while True:
            for server in self.servers:

                last_state = server.state
                server.state = server.is_alive

                if server.state:

                    self.watch(server)
                    if not last_state:
                        self.send_alarm(u'告警解除！',
                                        CANCELED_ALARM % dict(
                                            name=server.name, ip=server.ip))
                else:
                    if last_state:
                        self.send_alarm(
                            u'严重告警！',
                            ALARM_STR % dict(name=server.name, ip=server.ip))
                    continue

            time.sleep(self.interval)
