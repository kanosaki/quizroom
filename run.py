#!/usr/bin/env python

import os

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


def main():
    parse_command_line()
    application = quizhub.app.init_app()
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()