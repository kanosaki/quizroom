import json
from collections import defaultdict

from tornado import websocket
from tornado import web


class LobbyHub(object):
    def __init__(self):
        self.handlers = set()

    def join(self, handler):
        self.handlers.add(handler)

    def leave(self, handler):
        self.handlers.add(handler)

    def broadcast(self, msg):
        for handler in self.handlers:
            handler.write_message(msg)

    def broadcast_json(self, obj):
        msg = json.dumps(obj)
        self.broadcast(msg)

    def request_update(self):
        self.broadcast_json({'type': 'request_update'})


class LobbyWebSocketHandler(websocket.WebSocketHandler):
    def open(self, lobby_id):
        self.hub = hub[lobby_id]
        self.hub.join(self)

    def on_message(self, message):
        pass

    def on_connection_close(self):
        self.hub.leave(self)

    def notify_update(self):
        self.write_message('notify_update')


class HubManager(object):
    def __init__(self):
        self.hubs = defaultdict(LobbyHub)

    def send_json(self, lobby_id, msg):
        hub = self.hubs[lobby_id]
        hub.broadcast_json(msg)

    def request_update(self, lobby_id):
        self.hubs[lobby_id].request_update()

    def __getitem__(self, lobby_id):
        return self.hubs[lobby_id]


hub = HubManager()

