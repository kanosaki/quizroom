import json
from collections import defaultdict
import logging

from tornado import websocket


class LobbyHub(object):
    def __init__(self):
        self.handlers = set()

    def join(self, handler):
        self.handlers.add(handler)
        logging.info("JOIN handlers are now ", len(self.handlers))

    def leave(self, handler):
        logging.info("LEAVE handlers are now ", len(self.handlers))
        self.handlers.add(handler)

    def broadcast(self, msg):
        for handler in self.handlers:
            handler.write_message(msg)

    def broadcast_json(self, obj):
        logging.info("Broadcasting", obj, len(self.handlers), "handlers.")
        msg = json.dumps(obj)
        self.broadcast(msg)

    def request_update(self):
        self.broadcast_json({'type': 'request_update'})


class LobbyWebSocketHandler(websocket.WebSocketHandler):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.hub = None
        self.lobby_id = None

    def open(self, lobby_id):
        self.lobby_id = int(lobby_id)
        self.hub = hub[self.lobby_id]
        self.hub.join(self)

    def on_message(self, message):
        print(message)

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

