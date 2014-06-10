#!/usr/bin/env python

import os

import django.core.handlers.wsgi
from tornado.options import options, define, parse_command_line
import tornado.httpserver
import tornado.ioloop
import tornado.wsgi
import tornado.web
import quizroom.settings

from quizhub.dispatch import RootDispatcher

define('port', type=int, default=8000)
define('static_path', type=str, default=quizroom.settings.STATIC_ROOT)


def main():
    parse_command_line()
    os.environ["DJANGO_SETTINGS_MODULE"] = 'quizroom.settings'
    django_app = tornado.wsgi.WSGIContainer(
        django.core.handlers.wsgi.WSGIHandler()
    )
    application = tornado.web.Application([
        (r'/hub/.*', RootDispatcher),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': options.static_path}),
        (r'.*', tornado.web.FallbackHandler, dict(fallback=django_app)),
    ], debug=True)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()