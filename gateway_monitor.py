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

from monitor import Monitor
from logger import logger
from utils.singletion import Singleton

ALARM_STR = """\
严重告警：
    网关服到服务器 %(to_server)s 的连接已断开！
    
详情：
    服务器：        %(name)s
    IP地址：        %(ip)s
    项目路径：       %(project)s
"""

CANCEL_ALARM = """\
告警解除！

以下是原始告警信息：
***********************************************************
    严重告警：
        网关服到服务器 %(to_server)s 的连接已断开！
        
    详情：
        服务器：        %(name)s
        IP地址：        %(ip)s
        项目路径：       %(project)s
"""


class GatewayMonitor(Monitor, Singleton):
    last_states = []
    shell = """\
cd %(project)s;\
http=`grep httpPort dist/Gateway/config/config|grep -v '^#'|awk -F '=' '{print $NF}'|sed 's/[[:space:]]//g'`;\
activity=`grep localPort4 dist/Gateway/config/config|grep -v '^#'|awk -F '=' '{print $NF}'|sed 's/[[:space:]]//g'`;\
playback=`grep localPort3 dist/Gateway/config/config|grep -v '^#'|awk -F '=' '{print $NF}'|sed 's/[[:space:]]//g'`;\
chat=`grep localPort2 dist/Gateway/config/config|grep -v '^#'|awk -F '=' '{print $NF}'|sed 's/[[:space:]]//g'`;\
if [ `netstat -ntup|grep $activity|wc -l` -eq 0 ];then \
curl '127.0.0.1:$http/data?cmd=1&data=activityServer' &>/dev/null;\
sleep 0.5;\
a_state=`netstat -ntup|grep $activity|wc -l`;\
else \
a_state='1';\
fi;\
if [ `netstat -ntup|grep $playback|wc -l` -eq 0 ];then \
curl '127.0.0.1:$http/data?cmd=1&data=playbackServer' &>/dev/null;\
sleep 0.5;\
p_state=`netstat -ntup|grep $playback|wc -l`;\
else \
p_state='1';\
fi;\
if [ `netstat -ntup|grep $chat|wc -l` -eq 0 ];then \
curl '127.0.0.1:$http/data?cmd=1&data=chatServer' &>/dev/null;\
sleep 0.5;\
c_state=`netstat -ntup|grep $chat|wc -l`;\
else c_state='1';\
fi;\
echo {\\'ActivityServer\\': $a_state, \\'PlaybackServer\\': $p_state, \\'ChatServer\\': $c_state}
"""

    def get_last_state(self, server, project, obj):
        if self.last_states:
            for last_state in self.last_states:
                if last_state['server'] == \
                        server.name and last_state['project'] == \
                        project.path and last_state['obj'] == obj:
                    return last_state['state']
        return True

    def set_last_state(self, server, project, obj, state):
        if self.last_states:
            for last_state in self.last_states:
                if last_state['server'] == \
                        server.name and last_state['project'] == \
                        project.path and last_state['obj'] == obj:
                    last_state['state'] = state
                    return
        self.last_states.append({
            'server': server.name,
            'project': project.path,
            'obj': obj,
            'state': state
        })

    def watch(self, server):
        for project in server.projects:
            if project.is_maintenance:
                return

            logger.info(
                'check project - {} on server: {}'.format(
                    project.path, server.name))

            result = server.run_shell(self.shell % dict(project=project.path))[
                0].decode('utf8').strip()
            if not result:
                return

            r_dict = eval(result)

            for k, v in r_dict.items():
                last_state = self.get_last_state(server, project, k)
                state = True if v == 1 else False
                if state and not last_state:
                    self.send_alarm(u'告警解除！', CANCEL_ALARM % dict(
                        to_server=k,
                        name=server.name,
                        ip=server.ip,
                        project=project.path))
                elif not state and last_state:
                    self.send_alarm(u'严重告警！', ALARM_STR % dict(
                        to_server=k,
                        name=server.name,
                        ip=server.ip,
                        project=project.path))
                self.set_last_state(server, project, k, state)
