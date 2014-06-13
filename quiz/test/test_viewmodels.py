# -*- coding: utf-8 -*-
import json
from django.test import TestCase, Client

from quiz.control import active_lobby
from quiz.models import Participant


def decode_json(response):
    b = response.content
    return json.loads(b.decode('ascii'))


class TestParticipant(TestCase):
    fixtures = ['init_fixture.json']

    def test_register(self):
        c = Client()
        self.assertEqual(Participant.objects.count(), 0)
        url = '/user/register'
        res = c.post(url, {'name': 'test_user'})
        self.assertEqual(res.status_code, 302)
        self.assertEqual(Participant.objects.count(), 1)
        user = Participant.objects.get(pk=1)
        self.assertEqual(user.name, 'test_user')


class ActiveLobbyViewTest(TestCase):
    fixtures = ['init_fixture.json']

    def test_initialize_lobby(self):
        url = '/lobby/now'
        self.assertIsNone(active_lobby.get())
        c = Client()
        res = c.get(url)
        self.assertEqual(res.status_code, 200)  # No Lobby page
        self.assertRegex(res.content.decode('utf-8'), r'現在開催されているセッションはありません')

        res = decode_json(c.post(url, {'id': 'default'}))
        self.assertEqual(res['status'], 'ok')

        active_lobby_id = active_lobby.get().pk
        res = c.get(url)
        self.assertEqual(res.status_code, 302)  # Moved
        self.assertRegex(res.url, '/lobby/%d' % active_lobby_id)


class ControlLobbyTest(TestCase):
    fixtures = ['init_fixture.json']

    def setUp(self):
        control_url = '/lobby/now'
        c = Client()
        res = decode_json(c.post(control_url, {'id': 'default'}))
        self.assertEqual(res['status'], 'ok')

    def test_control_lobby(self):
        lobby = active_lobby.get()
        lobby_pk = lobby.pk
        url = '/lobby/control/%d' % lobby.pk
        c = Client()

        # Check initial state
        self.assertEqual(lobby.can_start, True)
        self.assertEqual(lobby.active_quiz, None)

        res = decode_json(c.post(url, {'command': 'activate'}))
        self.assertEqual(res['status'], 'ok')

        lobby = active_lobby.get()
        self.assertEqual(lobby.pk, lobby_pk)
        self.assertIsNotNone(lobby.active_quiz)
        self.assertFalse(lobby.can_start)
        self.assertEqual(lobby.active_quiz.body.caption, 'First quiz')

        res = decode_json(c.post(url, {'command': 'next'}))
        self.assertEqual(res['status'], 'ok')

        lobby = active_lobby.get()
        self.assertEqual(lobby.pk, lobby_pk)
        self.assertEqual(lobby.active_quiz.body.caption, 'Second quiz')


class TestViewLobby(TestCase):
    fixtures = ['init_fixture.json']

    def setUp(self):
        control_url = '/lobby/now'
        c = Client()
        res = decode_json(c.post(control_url, {'id': 'default'}))
        self.assertEqual(res['status'], 'ok')
        lobby = active_lobby.get()
        url = '/lobby/control/%d' % lobby.pk
        c = Client()

        # Check initial state
        self.assertEqual(lobby.can_start, True)
        self.assertEqual(lobby.active_quiz, None)

        res = decode_json(c.post(url, {'command': 'activate'}))
        self.assertEqual(res['status'], 'ok')

    def test_normal_post(self):
        pass
