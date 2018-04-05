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

import re

from monitor import Monitor
from logger import logger
from fuckpy.singleton import Singleton

ALARM_STR = """\
一般告警：
    硬盘剩余空间过低。

详情：
    服务器：        %(name)s
    IP地址：        %(ip)s
    设备：          %(device)s
    硬盘容量：       %(size)s
    硬盘已使用空间：  %(used)s
    硬盘可用空间：    %(avail)s
    硬盘使用率：      %(per)s
    硬盘挂载点：      %(mounted)s
"""

CANCEL_ALARM = """\
告警解除!

以下为原始告警信息.
***********************************************************
    一般告警：
        硬盘剩余空间过低。

    详情：
        服务器：        %(name)s
        IP地址：        %(ip)s
        设备：          %(device)s
        硬盘容量：       %(size)s
        硬盘已使用空间：  %(used)s
        硬盘可用空间：    %(avail)s
        硬盘使用率：      %(per)s
        硬盘挂载点：      %(mounted)s
"""


class DiskMonitor(Monitor, Singleton):
    last_states = []

    @staticmethod
    def get_disks(server):
        disks = []
        result = server.run_shell('df -h|tail -n +2')[0].decode('utf8').strip()
        if not result:
            return None
        for info in re.split(r'\n', result):
            device, size, used, vavil, used_percent, mounted_on = re.split(
                r'[\s]+', info)
            disk = server.Disk(device, size, used, vavil, used_percent,
                               mounted_on)
            disks.append(disk)
        return disks

    def get_last_state(self, server, disk):
        if self.last_states:
            for last_state in self.last_states:
                if last_state['server'] == server.name and \
                        last_state['device'] == disk.device:
                    return last_state['state']
        return False

    def set_last_state(self, server, disk):
        if self.last_states:
            for last_state in self.last_states:
                if last_state['server'] == server.name and \
                        last_state['device'] == disk.device:
                    last_state['state'] = disk.is_less
                    return
        self.last_states.append({
            'server': server.name,
            'device': disk.device,
            'state': disk.is_less
        })

    def watch(self, server):
        disks = self.get_disks(server)
        if not disks:
            return

        logger.info('check server: {}'.format(server.name))

        for disk in disks:
            last_state = self.get_last_state(server, disk)
            if disk.is_less and not last_state:
                self.send_alarm(u'一般告警！', ALARM_STR % dict(
                    name=server.name,
                    ip=server.ip,
                    device=disk.device,
                    size=disk.size,
                    used=disk.used,
                    avail=disk.avail,
                    per=disk.use_percent,
                    mounted=disk.mounted_on))
            elif not disk.is_less and last_state:
                self.send_alarm(u'告警消除！', CANCEL_ALARM % dict(
                    name=server.name,
                    ip=server.ip,
                    device=disk.device,
                    size=disk.size,
                    used=disk.used,
                    avail=disk.avail,
                    per=disk.use_percent,
                    mounted=disk.mounted_on))
            self.set_last_state(server, disk)
