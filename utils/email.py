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

import smtplib
import email.mime.multipart
import email.mime.text


class Email(object):
    server = None
    port = None
    username = None
    passwd = None
    mailto = None

    def __init__(self, subject, content):
        self.subject = subject
        self.content = content

    @classmethod
    def setup(cls, server, port, username, passwd, mailto):
        cls.server = server
        cls.port = port
        cls.username = username
        cls.passwd = passwd
        cls.mailto = mailto

    def send(self):
        msg = email.mime.multipart.MIMEMultipart()
        msg['from'] = Email.username
        msg['to'] = ','.join(Email.mailto)
        msg['subject'] = self.subject
        content = self.content
        txt = email.mime.text.MIMEText(content)
        msg.attach(txt)
        smtp = smtplib.SMTP_SSL(Email.server, Email.port)
        smtp.ehlo()
        smtp.login(Email.username, Email.passwd)
        smtp.sendmail(Email.username, self.mailto, str(msg))
        smtp.close()
