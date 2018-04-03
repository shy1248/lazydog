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

import yaml

from server import Server
from lazydog import logger

HTTPD_PORT = None
DEF_PASSWD = None
DISK_THRESOLD = None
SERVERS = []
DISK_MONI_INTERV = None
PRO_MONI_INTERV = None
GATE_MONI_INTERV = None
SMTP_SER = None
SMTP_PORT = None
SMTP_USER = None
SMTP_PASS = None
MAIL_TO = None

def load_conf(conf_file):
    if conf_file:

        file = open(conf_file)
        conf = yaml.load(file)
        print(conf)

        global HTTPD_PORT
        global DEF_PASSWD
        global DISK_THRESOLD
        global DISK_MONI_INTERV
        global PRO_MONI_INTERV
        global GATE_MONI_INTERV
        global SMTP_SER
        global SMTP_PORT
        global SMTP_USER
        global SMTP_PASS
        global MAIL_TO
        global SERVERS

        try:
            HTTPD_PORT = conf['http_port']
            DEF_PASSWD = conf['default_passwd']
            DISK_MONI_INTERV = conf['disk_threshold']
            DISK_MONI_INTERV = conf['monitors']['disk_monitor']
            PRO_MONI_INTERV = conf['monitors']['progress_monitor']
            GATE_MONI_INTERV = conf['monitors']['gateway_monitor']
            SMTP_SER = conf['email']['server']
            SMTP_PORT = conf['email']['port']
            SMTP_USER = conf['email']['username']
            SMTP_PASS = conf['email']['passwd']
            MAIL_TO = conf['email']['mailto']
            servers_info = conf['servers']
            for server_info in servers_info:
                projects = []
                for project_info in server_info['projects']:
                    project = Server.Project(project_info['path'],
                                               project_info['port'])
                    projects.append(project)

                server = Server(
                    name=server_info['name'],
                    ip=server_info['ip'],
                    projects=projects,
                    passwd=server_info['passwd'],
                    default_passwd=DEF_PASSWD)
                SERVERS.append(server)
        except Exception as e:
            logger.error(
                'load config file error! details:\n{e}'.format(e=e))
        file.close()
    else:
        logger.error('Cound not found config file!')
