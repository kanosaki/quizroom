# -*- coding: utf-8 -*-

from django.conf import settings

from quiz.models import Lobby, KVS


DEFAULT_ACTIVE_LOBBY_KEY = 'active_lobby_pk'


class LobbyControl(object):
    def __init__(self, db_path=settings.CONTROL_LEVELDB, active_lobby_key=DEFAULT_ACTIVE_LOBBY_KEY):
        self.active_lobby_key = active_lobby_key

    def get(self):
        try:
            lobby_pk = KVS.get(self.active_lobby_key)
            return Lobby.objects.get(pk=lobby_pk)
        except KeyError:
            return None

    def set(self, lobby_pk):
        KVS.put(self.active_lobby_key, lobby_pk)

    # TODO: クライアントに参加者一覧の更新を通知したり
    def trigger_client_joined(self):
        pass

    # TODO: クライアントへクイズが次のものへ移ることを通知します
    def trigger_next_quiz(self):
        pass

    def trigger_room_opened(self):
        pass

    # TODO: 一連のクイズを終了し，スコア画面等に遷移します
    def trigger_room_closed(self):
        pass

active_lobby = LobbyControl()
