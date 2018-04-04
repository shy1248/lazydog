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

from utils.resty import PathDispatcher, Resty
import httphandler
from logger import logger

if __name__ == '__main__':

    import config
    conf, disk_monitor, progress_monitor, gateway_monitor = config.load()
    logger.info('starting disk_monitor thread ...')
    disk_monitor.start()
    logger.info('starting progress_monitor thread ...')
    progress_monitor.start()
    logger.info('starting gateway_monitor thread ...')
    gateway_monitor.start()

    # start http server
    httpd_port = conf['http_port']
    logger.info('Starting server with port {} ...'.format(httpd_port))
    dispatcher = PathDispatcher()
    dispatcher.regist('POST', '/resty', httphandler.rest_hand)
    resty = Resty(dispatcher)
    resty.listen(httpd_port)
