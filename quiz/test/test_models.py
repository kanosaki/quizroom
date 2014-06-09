# -*- coding: utf-8 -*-

from django.utils import timezone

from django.test import TestCase

from quiz.models import Lobby, KVS
from quiz.control import active_lobby


class TestLobby(TestCase):
    fixtures = ['init_fixture.json']

    def setUp(self):
        first_lobby = Lobby.objects.get(pk=1)
        active_lobby.set(first_lobby)

    def test_lobby_sequential(self):
        lobby = active_lobby.get()
        self.assertEqual(lobby.started_time, None)
        self.assertEqual(lobby.finished_time, None)
        self.assertEqual(lobby.can_start, True)
        self.assertIsNone(lobby.active_quiz)

        before_start = timezone.now()
        lobby.start()
        after_start = timezone.now()
        self.assertTrue(before_start < lobby.started_time < after_start)
        self.assertIsNotNone(lobby.active_quiz)
        self.assertFalse(lobby.can_start)
        self.assertEqual(lobby.active_quiz.body.caption, "First quiz")

        # すでに始まっているゲームの開始は許可しない
        with self.assertRaises(RuntimeError):
            lobby.start()

        # 次の問題へ
        lobby.go_next_quiz()
        self.assertEqual(lobby.active_quiz.body.caption, "Second quiz")


class TestKVS(TestCase):

    def test_kvs(self):
        with self.assertRaises(KeyError):
            KVS.get('hogehoge')

        KVS.put('hoge', 'fuga')
        self.assertEqual('fuga', KVS.get('hoge'))
        KVS.put('hoge', 'foo')
        self.assertEqual('foo', KVS.get('hoge'))
