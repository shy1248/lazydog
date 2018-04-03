#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: yushuibo
@Copyright (c) 2018 yushuibo. All rights reserved.
@Licence: GPL-2
@Email: hengchen2005@gmail.com
@Create: logger.py
@Last Modified: 2018/4/1 22:13
@Desc: logging config
"""

import logging
from logging import handlers

_FORMAT = '%(asctime)s-[%(levelname)s]-%(name)s.%(module)s@line %(lineno)d: '\
          '%(message)s'


def init(filename=None):
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(_FORMAT)

    # print to screen
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    logger.addHandler(console)

    if filename is not None:
        # write to log file
        # fh = logging.FileHandler(file)
        file = handlers.TimedRotatingFileHandler(filename, when='D',
                                                 interval=1, backupCount=3,
                                                 encoding='utf8')
        file.setLevel(logging.INFO)
        # set the format for record
        file.setFormatter(formatter)
        logger.addHandler(file)

    return logger


if __name__ == '__main__':
    logger = init(filename='test.log')
    logger.info('Logging example ...')
