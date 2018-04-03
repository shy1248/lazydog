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

import threading

import paramiko

from lazydog import logger
from utils.ping import Ping


class Server(object):
    def __init__(self, name, ip, projects, passwd, default_passwd):
        self.name = name
        self.ip = ip
        self.projects = projects
        self.disks = None
        self.user = 'root'
        self.passwd = passwd if passwd else default_passwd
        self.state = True
        self._lock = threading.Lock()

    def _connect(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        with self._lock:
            try:
                ssh.connect(self.ip, 22, self.user, self.passwd)
            except Exception as e:
                logger.error(
                    'ssh connection error! details:\n{e}'.format(e=e))
                return None
        return ssh

    @staticmethod
    def _disconnect(ssh):
        ssh.close()

    def run_shell(self, shell_str):
        ssh = self._connect()
        if ssh:
            stdin, stdout, stderr = ssh.exec_command(shell_str)
            result = stdout.read(), stderr.read()
            self._disconnect(ssh)
            return result
        return None

    @property
    def is_alive(self):
        ping = Ping(1)
        resp = ping.send(self.ip)
        return True if resp else False

    def any_project_has_port(self):
        for project in self.projects:
            if project.has_port():
                return True
        return False

    class Project(object):
        def __init__(self, path, port):
            self.path = path
            self.port = port
            self.is_maintenance = False
            self.is_alive = True

        def has_port(self):
            return True if self.port else False

    class Disk(object):
        threshold = 0

        @classmethod
        def set_threshold(cls, threshold):
            cls.threshold = threshold if threshold else 75

        def __init__(self, device, size, used, avail, use_percent, mounted_on):
            self.device = device
            self.size = size
            self.used = used
            self.avail = avail
            self.use_percent = use_percent
            self.mounted_on = mounted_on

        @property
        def is_less(self):
            return False if int(
                self.use_percent.strip('%')) < self.threshold else True
