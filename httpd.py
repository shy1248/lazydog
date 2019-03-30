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
from fuckpy.resty import PathDispatcher, Resty

import config
from logger import logger
from monitor import Monitor

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


def refresh_conf():
    conf, *_ = config.load()
    return "Reload conf: \n{}\n".format(conf).encode('utf8')


def set_project_status(ip, path):
    g_server = (server for server in config.SERVERS if server.ip == ip)
    server = next(g_server)
    projects = server.projects
    g_project = (project for project in projects if project.path == path)
    project = next(g_project)
    last_status = project.is_maintenance
    project.is_maintenance = not last_status
    if project.is_maintenance and not last_status:
        Monitor.send_alarm(u'通知！', MANI_STR % dict(
            name=server.name,
            ip=server.ip,
            project=project.path,
            port=project.port))
    elif not project.is_maintenance and last_status:
        Monitor.send_alarm(u'通知！', PREW_STR % dict(
            name=server.name,
            ip=server.ip,
            project=project.path,
            port=project.port))
    return 'Project \'{}\' on server \'{}\' is change to {} status.\n'.format(
        project.path, server.ip, 'Maintenance'
        if project.is_maintenance else 'Prowork').encode('utf8')


@PathDispatcher.post('/resty')
def restyhandler(environ, start_response):
    start_response('200 OK', [('content-type', 'text/plain')])
    addr = environ['REMOTE_ADDR']
    params = environ['params']
    logger.info("Get post data: {} from host: {}".format(params, addr))
    if 'cmd' in params.keys():
        # reload conf file
        if params['cmd'] == '1':
            yield refresh_conf()
        # change project's status
        elif params['cmd'] == '2' and 'project' in params.keys():
            yield set_project_status(addr, params['project'])
        else:
            yield "Error parameters: {}".format(
                json.dumps(params)).encode('utf8')
    else:
        yield "Error parameters: {}".format(json.dumps(params)).encode('utf8')


class Httpd(object):
    def __init__(self, port):
        self.port = port

    def start(self):
        logger.info('Starting http sever with port: {}'.format(self.port))
        resty = Resty('lazydog')
        resty.listen(self.port)
