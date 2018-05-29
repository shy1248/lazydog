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

# from httpd import Httpd
from logger import logger

if __name__ == '__main__':
    import config

    conf, disk_monitor, progress_monitor, gateway_monitor, db_conn_monitor = config.load()
    logger.info('starting disk_monitor thread ...')
    disk_monitor.start()
    logger.info('starting progress_monitor thread ...')
    progress_monitor.start()
    logger.info('starting gateway_monitor thread ...')
    gateway_monitor.start()
    logger.info('starting db_connection_monitor thread ...')
    db_conn_monitor.start()

    # httpd_port = conf['http_port']
    # httpd = Httpd(httpd_port)
    # httpd.start()
