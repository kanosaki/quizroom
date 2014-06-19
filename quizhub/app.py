import os

import django.core.handlers.wsgi
import tornado
from tornado.options import options

from quizhub.lobby import LobbyWebSocketHandler


def init_app():
    os.environ["DJANGO_SETTINGS_MODULE"] = options.django_settings
    django_app = tornado.wsgi.WSGIContainer(
        django.core.handlers.wsgi.WSGIHandler()
    )
    application = tornado.web.Application([
        (r'/ws/lobby/(?P<lobby_id>.+)', LobbyWebSocketHandler),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': options.static_path}),
        (r'.*', tornado.web.FallbackHandler, dict(fallback=django_app)),
    ])
    return application
