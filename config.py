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

from os.path import abspath, dirname, join

import yaml
from fuckpy.email_ import Email

from db_monitor import DbConnMonitor
from disk_monitor import DiskMonitor
from gateway_monitor import GatewayMonitor
from logger import logger
from progress_monitor import ProgressMonitor
from server import Server

conf_file = join(abspath(dirname(__file__)), 'lazydog.yml')
SERVERS = None


def load():
    if conf_file:
        file = open(conf_file)
        conf = yaml.load(file)
        try:
            default_password = conf['default_passwd']
            disk_thresold = conf['disk_threshold']
            disk_monitor_interval = conf['monitors']['disk_monitor']
            progress_monitor_interval = conf['monitors']['progress_monitor']
            gateway_monitor_interval = conf['monitors']['gateway_monitor']
            db_conn_monitor_interval = conf['monitors']['db_conn_monitor']
            smtp_server = conf['email']['server']
            smtp_port = conf['email']['port']
            smtp_username = conf['email']['username']
            smtp_password = conf['email']['passwd']
            mailto_list = conf['email']['mailto']
            servers_info = conf['servers']

            servers = []
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
                    default_passwd=default_password)

                servers.append(server)

            global SERVERS
            SERVERS = servers

            # initilize
            Server.Disk.set_threshold(disk_thresold)
            Email.setup(smtp_server, smtp_port, smtp_username, smtp_password,
                        mailto_list)
            disk_monitor = DiskMonitor(disk_monitor_interval)
            progress_monitor = ProgressMonitor(progress_monitor_interval)
            gateway_monitor = GatewayMonitor(gateway_monitor_interval)
            db_conn_monitor = DbConnMonitor(db_conn_monitor_interval)

            # clear cache
            disk_monitor.servers.clear()
            progress_monitor.servers.clear()
            gateway_monitor.servers.clear()
            # recache
            for server in servers:
                disk_monitor.servers.append(server)
                if server.any_project_has_port():
                    progress_monitor.servers.append(server)
                if 'gate' in server.name:
                    gateway_monitor.servers.append(server)
                if 'db' in server.name or 'datacenter' in server.name:
                    db_conn_monitor.servers.append(server)

            return conf, disk_monitor, progress_monitor, gateway_monitor, db_conn_monitor
        except Exception as e:
            logger.error('load config file error! details:\n{e}'.format(e=e))
            return None
        finally:
            file.close()
    else:
        logger.error('Cound not found config file!')
        return None
