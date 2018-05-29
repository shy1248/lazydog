#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: yushuibo
@Copyright (c) 2018 yushuibo. All rights reserved.
@Licence: GPL-2
@Email: hengchen2005@gmail.com
@Create: DbConnMonitor.py
@Last Modified: 2018/5/29 上午 10:03
@Desc: --
"""

from fuckpy.singleton import Singleton
from logger import logger
from monitor import Monitor

ALARM_STR = """\
严重告警：
    数据库连接数量过多！

详情：
    服务器：          %(name)s
    IP地址：          %(ip)s
    当前连接数：       %(num)s
"""

CANCEL_ALARM = """\
告警解除！

以下是原始告警信息：
***********************************************************
    严重告警：
        数据库连接数量过多！

    详情：
        服务器：          %(name)s
        IP地址：          %(ip)s
        当前连接数：       %(num)s
"""


class DbConnMonitor(Monitor, Singleton):
    last_status = {}
    shell = "netstat -ntup|awk '{print $4}'|grep 3306|wc -l"

    def get_last_status(self, server):
        if server.name in self.last_status:
            return self.last_status[server.name]
        return False

    def set_last_status(self, server, state):
        self.last_status[server.name] = state

    def watch(self, server):
        logger.info('check server: {}'.format(server.name))

        result = server.run_shell(self.shell)[0].decode(
            'utf8').strip()
        print(result)

        if int(result) >= 200 and not self.get_last_status(server):
            self.set_last_status(server, True)

            self.send_alarm(u'一般告警！', ALARM_STR % dict(
                name=server.name,
                ip=server.ip,
                num=result))
        elif int(result) < 200 and self.get_last_status(server):
            self.set_last_status(server, False)

            self.send_alarm(u'告警解除！', CANCEL_ALARM % dict(
                name=server.name,
                ip=server.ip,
                num=result))
