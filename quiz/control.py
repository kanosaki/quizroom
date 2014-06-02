# -*- coding: utf-8 -*-

from django.conf import settings
import leveldb

from quiz.models import Robby


default_db = leveldb.LevelDB(settings.CONTROL_LEVELDB)

DEFAULT_ACTIVE_ROBBY_KEY = 'active_robby_pk'


class RobbyControl(object):
    def __init__(self, db=default_db, active_robby_key=DEFAULT_ACTIVE_ROBBY_KEY):
        self.active_robby_key = active_robby_key
        self.db = db

    def get(self):
        try:
            robby_pk = self.db.Get(self.active_robby_key)
            return Robby.objects.get(pk=robby_pk)
        except KeyError:
            if settings.DEBUG:
                self.set('1')
            return None

    def set(self, robby_pk):
        self.db.Put(self.active_robby_key, robby_pk)

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

active_robby = RobbyControl()
