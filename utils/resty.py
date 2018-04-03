#!usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: yushuibo
@Copyright (c) 2018 yushuibo. All rights reserved.
@Licence: GPL-2
@Email: hengchen2005@gmail.com
@File: resty.py
@Create: 2018-04-01 16:45:48
@Last Modified: 2018-04-01 16:45:48
@Desc: --
"""

import cgi
import weakref
from wsgiref.simple_server import make_server

_notfound_resp="""\
<html>
<title>Page Not Found!</title>
<body>
<p>404, Page Not Found!</p>
</body>
</html>
"""
def notfound_404(environ, start_response):
    start_response('404 Not Found', [('content-type', 'text/html')])
    yield _notfound_resp.encode('utf-8')


class CachedRestyManager(object):
    def __init__(self):
        self._cache = weakref.WeakKeyDictionary()

    def get_instance(self, dispatcher):
        if dispatcher not in self._cache:
            instance = Resty(dispatcher)
            self._cache[dispatcher] = instance
        else:
            instance = self._cache[dispatcher]
        return instance

    def clear(self):
        self._cache.clear()


class Resty(object):
    manager = CachedRestyManager()
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    def get_instance(self, dispatcher):
        return Resty.manager.get_instance(dispatcher)

    def listen(self, port):
        httpd = make_server('', port, self.dispatcher)
        httpd.serve_forever()


class PathDispatcher(object):
    def __init__(self):
        self.pathmap = {}

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']
        params = cgi.FieldStorage(environ['wsgi.input'], environ=environ)
        method = environ['REQUEST_METHOD'].lower()
        environ['params'] = {key: params.getvalue(key) for key in params}
        handler = self.pathmap.get((method, path), notfound_404)
        return handler(environ, start_response)

    def register(self, method, path, func):
        self.pathmap[method.lower(), path] = func
        return func


if __name__ == '__main__':

    def default(environ, start_response):
        start_response('200 OK', [('content-type', 'text/html')])
        yield b'Hello, WSGI!'

    dispatcher = PathDispatcher()
    dispatcher.register('GET', '/hello', default)
    resty = Resty(dispatcher)
    resty.listen(8080)
