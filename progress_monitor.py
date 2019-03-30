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

from logger import logger
from monitor import Monitor
from fuckpy.singleton import Singleton

ALARM_STR = """\
严重告警：
    项目停止服务。

详情：
    服务器：        %(name)s
    IP地址：        %(ip)s
    项目路径：       %(project)s
    检查端口：       %(port)s
"""

CANCEL_ALARM = """\
告警解除！

以下是原始告警信息：
***********************************************************
严重告警：
    项目停止服务。

详情：
    服务器：        %(name)s
    IP地址：        %(ip)s
    项目路径：       %(project)s
    检查端口：       %(port)s
"""


class ProgressMonitor(Monitor, Singleton):
    def watch(self, server):
        for project in server.projects:
            if project.is_maintenance:
                return

            logger.info(
                'check project - {} with port - {} on server: {}'.format(
                    project.path, project.port, server.name))

            last_state = project.is_alive
            shell = 'netstat -lntup|grep {}|wc -l'.format(project.port)
            result = server.run_shell(shell)[0].decode('utf8').strip()
            if not result:
                return
            project.is_alive = True if not result == '0' else False

            if not project.is_alive and last_state:
                self.send_alarm(u'严重告警！', ALARM_STR % dict(
                    name=server.name,
                    ip=server.ip,
                    project=project.path,
                    port=project.port))
            elif project.is_alive and not last_state:
                self.send_alarm(u'告警解除！', CANCEL_ALARM % dict(
                    name=server.name,
                    ip=server.ip,
                    project=project.path,
                    port=project.port))
