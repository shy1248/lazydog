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

import json

import server
import config
from lazydog import logger

MANI_STR = """\
通知：
    项目已被置为维护状态，已停止监控。
    
详情：
    服务器：        %(name)s
    IP地址：        %(ip)s
    项目路径：       %(project)s
    检测端口：       %(port)s
"""

PREW_STR = """\
通知：
    项目已恢复为服务状态，开始监控。
    
详情：
    服务器：        %(name)s
    IP地址：        %(ip)s
    项目路径：       %(project)s
    检测端口：       %(port)s
"""

def change_project_state(environ, start_response):
    start_response('200 OK', [('content-type', 'text/plain')])
    addr = environ['REMOTE_ADDR']
    params = environ['params']
    logger.info("Get post data: {} from host: {}".format(params, addr))
    yield json.dumps(params).encode('utf8')
    # for server in self.servers:
    #     if server.ip == ip:
    #         for project in server.projects:
    #             if project.path == path:
    #                 last_state = project.is_maintenance
    #                 project.is_maintenance = True if status == 1 else False
    #                 if project.is_maintenance and not last_state:
    #                     monitor.Monitor.send_alarm(u'通知！',
    #                                                MANI_STR % dict(
    #                                                    name=server.name,
    #                                                    ip=server.ip,
    #                                                    project=project.path,
    #                                                    port=project.port))
    #                 elif not project.is_maintenance and last_state:
    #                     monitor.Monitor.send_alarm(u'通知！',
    #                                                PREW_STR % dict(
    #                                                    name=server.name,
    #                                                    ip=server.ip,
    #                                                    project=project.path,
    #                                                    port=project.port))

    # Test function
    def change_disk_treshold(self, status):
        if status == 0:
            server.Server.Disk.set_threshold(75)
        else:
            server.Server.Disk.set_threshold(10)

    def change_ip(self, status):
        if status == 0:
            for server in self.servers:
                if server.name == 'gate01-cc':
                    server.ip = '58.87.80.120'
        else:
            for server in self.servers:
                if server.name == 'gate01-cc':
                    server.ip = '58.87.71.208'

