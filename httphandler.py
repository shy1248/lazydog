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

from logger import logger

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

servers = []

def rest_hand(environ, start_response):
    start_response('200 OK', [('content-type', 'text/plain')])
    addr = environ['REMOTE_ADDR']
    params = environ['params']
    logger.info("Get post data: {} from host: {}".format(params, addr))

    if 'cmd' in params.keys():
        # reload conf file
        if params['cmd'] == '1':
            import config
            conf, *_ = config.load()
            yield "Reload conf: {}".format(conf).encode('utf8')

        # set project status in maintenance
        elif params['cmd'] == '2' and 'project' in params.keys():
            for server in servers:
                if server.ip == addr:
                    for project in server.projects:
                        if project.path == params['project'].replace('\'', ''):
                            last_status = project.is_maintenance
                            project.is_maintenance = not last_status
                            yield 'Project {} on server {} is change to {} status.'.format(
                                params['project'], addr,
                                'Prowork' if not project.is_maintenance else 'Maintenance').encode(
                                'utf8')
        yield "Error parameters: {}".format(json.dumps(params)).encode('utf8')
