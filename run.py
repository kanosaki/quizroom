#!/usr/bin/env python3

import os
import logging
from logging.handlers import RotatingFileHandler

from tornado.options import options, define, parse_command_line
import tornado.httpserver
import tornado.ioloop
import tornado.wsgi
import tornado.web

import quizroom.settings
import quizhub.app


define('port', type=int, default=8000)
define('static_path', type=str, default=quizroom.settings.STATIC_ROOT)
define('django_settings', type=str, default='quizroom.settings')

define('app_log', type=str, default='log/app.log')
define('gen_log', type=str, default='log/gen.log')
define('access_log', type=str, default='log/access.log')


def init_logger():
    access_log = logging.getLogger('tornado.access')
    app_log = logging.getLogger('tornado.application')
    gen_log = logging.getLogger('tornado.general')
    access_log.addHandler(RotatingFileHandler(options.access_log))
    app_log.addHandler(RotatingFileHandler(options.app_log))
    gen_log.addHandler(RotatingFileHandler(options.gen_log))


def main():
    os.environ["DJANGO_SETTINGS_MODULE"] = options.django_settings
    parse_command_line()
    application = quizhub.app.init_app()
    http_server = tornado.httpserver.HTTPServer(application)
    init_logger()
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
