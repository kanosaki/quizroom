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
        self.assertEqual(None, lobby.current_state)
        self.assertIsNone(lobby.active_quiz)

        before_start = timezone.now()
        lobby.initialize()
        after_start = timezone.now()
        self.assertTrue(before_start < lobby.started_time < after_start)
        self.assertIsNone(lobby.active_quiz)
        self.assertEqual(lobby.current_state, 'INACTIVE')

        lobby.go_next_quiz()
        self.assertEqual("First quiz", lobby.active_quiz.body.caption)
        self.assertEqual(lobby.current_state, 'QUIZ_OPENED')
        lobby.close_participant_submission()
        self.assertEqual(lobby.current_state, 'MASTER_ANSWERING')
        lobby.close_master_submission()
        self.assertEqual(lobby.current_state, 'SHOWING_ANSWER')
        lobby.show_scores()
        self.assertEqual(lobby.current_state, 'SHOWING_SCORE')

        # 次の問題へ
        lobby.go_next_quiz()
        self.assertEqual(lobby.current_state, 'QUIZ_OPENED')
        self.assertEqual("Second quiz", lobby.active_quiz.body.caption)


class TestKVS(TestCase):

    def test_kvs(self):
        with self.assertRaises(KeyError):
            KVS.get('hogehoge')

        KVS.put('hoge', 'fuga')
        self.assertEqual('fuga', KVS.get('hoge'))
        KVS.put('hoge', 'foo')
        self.assertEqual('foo', KVS.get('hoge'))
