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


from utils import log
logger = log.init(filename='./lazydog.log')

if __name__ == '__main__':

    import config
    config.load_conf('./lazydog.yml')

    from server import Server
    from utils.email import Email
    from disk_monitor import DiskMonitor
    from progress_monitor import ProgressMonitor
    from gateway_monitor import GatewayMonitor

    Server.Disk.set_threshold(config.DISK_THRESOLD)

    Email.setup(config.SMTP_SER, config.SMTP_PORT,
                config.SMTP_USER, config.SMTP_PASS,
                config.MAIL_TO)

    disk_monitor = DiskMonitor(config.DISK_MONI_INTERV)
    progress_monitor = ProgressMonitor(config.PRO_MONI_INTERV)
    gateway_monitor = GatewayMonitor(config.GATE_MONI_INTERV)

    for server in config.SERVERS:
        disk_monitor.servers.append(server)
        if server.any_project_has_port():
            progress_monitor.servers.append(server)
        if 'gate' in server.name:
            gateway_monitor.servers.append(server)

    logger.info('starting disk_monitor thread ...')
    disk_monitor.start()
    logger.info('starting progress_monitor thread ...')
    progress_monitor.start()
    logger.info('starting gateway_monitor thread ...')
    gateway_monitor.start()

    # start http server
    logger.info(
        'starting http server with port {} ...'.format(
            config.HTTPD_PORT))
    import utils.resty as resty
    import httphandler

    dispatcher = resty.PathDispatcher()
    dispatcher.register('POST', '/serl', httphandler.change_project_state)
    resty = resty.Resty(dispatcher)
    resty.listen(config.HTTPD_PORT)
