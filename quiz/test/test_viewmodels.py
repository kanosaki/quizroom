# -*- coding: utf-8 -*-
import json

from django.test import TestCase, Client

from quiz.control import active_lobby
from quiz.models import Participant


# TODO: 単体テストになってないので，fixtureを分割して各テストを分離する

def decode_json(response):
    b = response.content
    return json.loads(b.decode('utf-8'))


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
        self.assertEqual(None, lobby.current_state)
        self.assertEqual(lobby.active_quiz, None)

        res = decode_json(c.post(url, {'command': 'activate'}))
        self.assertEqual(res['status'], 'ok')

        res = decode_json(c.post(url, {'command': 'next'}))
        self.assertEqual(res['status'], 'ok')
        lobby = active_lobby.get()
        self.assertEqual(lobby.pk, lobby_pk)
        self.assertIsNotNone(lobby.active_quiz)
        self.assertEqual(lobby.active_quiz.body.caption, 'First quiz')
        self.assertEqual('QUIZ_OPENED', lobby.current_state)
        res = decode_json(c.post(url, {'command': 'close_submission'}))
        self.assertEqual(res['status'], 'ok')
        lobby = active_lobby.get()
        self.assertEqual('MASTER_ANSWERING', lobby.current_state)
        res = decode_json(c.post(url, {'command': 'show_scores'}))
        self.assertEqual(res['status'], 'ok')
        lobby = active_lobby.get()
        self.assertEqual('SHOWING_SCORE', lobby.current_state)

        res = decode_json(c.post(url, {'command': 'next'}))
        self.assertEqual(res['status'], 'ok')

        lobby = active_lobby.get()
        self.assertEqual('QUIZ_OPENED', lobby.current_state)
        self.assertEqual(lobby.pk, lobby_pk)
        self.assertEqual(lobby.active_quiz.body.caption, 'Second quiz')


class TestViewLobby(TestCase):
    fixtures = ['init_fixture.json']

    def setUp(self):
        c = Client()
        res = decode_json(c.post('/lobby/now', {'id': 'default'}))
        self.assertEqual(res['status'], 'ok')
        lobby = active_lobby.get()
        control_url = '/lobby/control/%d' % lobby.pk
        c = Client()

        # Check initial state
        self.assertEqual(None, lobby.current_state)
        self.assertEqual(lobby.active_quiz, None)
        res = decode_json(c.post(control_url, {'command': 'activate'}))
        self.assertEqual(res['status'], 'ok')
        lobby = active_lobby.get()
        self.assertEqual('INACTIVE', lobby.current_state)
        self.assertIsNone(lobby.active_quiz)

        res = decode_json(c.post(control_url, {'command': 'next'}))
        self.assertEqual(res['status'], 'ok')
        lobby = active_lobby.get()
        self.assertIsNotNone(lobby.active_quiz)
        self.assertEqual(lobby.active_quiz.body.caption, 'First quiz')
        self.assertEqual('QUIZ_OPENED', lobby.current_state)
        self.url = '/lobby/%d' % lobby.pk

    def test_normal_post(self):
        c = Client()
        c.post('/user/register', {'name': 'test_user'})
        res = decode_json(c.post(self.url, {
            'command': 'submit_answer',
            'lobby_id': 1,
            'choice_id': 1,  # 1 point choice
        }))
        self.assertEqual(res['status'], 'ok', res.get('message'))
        res = decode_json(c.get(self.url, {'type': 'query', 'command': 'score_list'}))
        self.assertEqual(res['status'], 'ok', res.get('message'))
        self.assertEqual(res['content'], [
            {'score': 1,
             'rank': 1,
             'name': 'test_user',
             'participant_id': 1,
             'is_you': True}
        ])

    def test_multi_participant(self):
        c1 = Client()
        c2 = Client()

        c1.post('/user/register', {'name': 'test_user1'})
        c2.post('/user/register', {'name': 'test_user2'})

        res = decode_json(c1.post(self.url, {
            'command': 'submit_answer',
            'lobby_id': 1,
            'choice_id': 1,  # 1 point choice
        }))
        self.assertEqual(res['status'], 'ok', res.get('message'))
        res = decode_json(c2.post(self.url, {
            'command': 'submit_answer',
            'lobby_id': 1,
            'choice_id': 0,  # 0 point choice
        }))
        self.assertEqual(res['status'], 'ok', res.get('message'))

        res = decode_json(c1.get(self.url, {'type': 'query', 'command': 'score_list'}))
        self.assertEqual(res['status'], 'ok', res.get('message'))
        self.assertEqual(res['content'], [
            {'score': 1,
             'rank': 1,
             'name': 'test_user1',
             'participant_id': 1,
             'is_you': True},
            {'score': 0,
             'rank': 2,
             'name': 'test_user2',
             'participant_id': 2,
             'is_you': False},
        ])

        res = decode_json(c2.get(self.url, {'type': 'query', 'command': 'score_list'}))
        self.assertEqual(res['status'], 'ok', res.get('message'))
        self.assertEqual(res['content'], [
            {'score': 1,
             'rank': 1,
             'name': 'test_user1',
             'participant_id': 1,
             'is_you': False},
            {'score': 0,
             'rank': 2,
             'name': 'test_user2',
             'participant_id': 2,
             'is_you': True},
        ])
