# -*- coding: utf-8 -*-

from django.test import TestCase, Client

from quiz.control import active_lobby


class ActiveLobbyViewTest(TestCase):
    fixtures = ['init_fixture.json']

    def test_initialize_lobby(self):
        url = '/lobby/now'
        self.assertIsNone(active_lobby.get())
        c = Client()
        res = c.get(url)
        self.assertEqual(res.status_code, 200)  # No Lobby page
        self.assertRegexpMatches(res.content, r'現在開催されているセッションはありません')

        res = c.post(url, {'id': 'default'})
        self.assertJSONEqual(res.content, {
            u'status': u'ok',
            u'message': u'Active lobby set to Lobby 1',
            })

        active_lobby_id = active_lobby.get().pk
        res = c.get(url)
        self.assertEqual(res.status_code, 302)  # Moved
        self.assertRegexpMatches(res.url, '/lobby/%d' % active_lobby_id)


class ControlLobbyTest(TestCase):
    fixtures = ['init_fixture.json']

    def setUp(self):
        control_url = '/lobby/now'
        c = Client()
        res = c.post(control_url, {'id': 'default'})
        self.assertJSONEqual(res.content, {
            u'status': u'ok',
            u'message': u'Active lobby set to Lobby 1',
        })

    def test_control_lobby(self):
        lobby = active_lobby.get()
        lobby_pk = lobby.pk
        url = '/lobby/control/%d' % lobby.pk
        c = Client()

        # Check initial state
        self.assertEqual(lobby.can_start, True)
        self.assertEqual(lobby.active_quiz, None)

        res = c.post(url, {'command': 'activate'})
        self.assertJSONEqual(res.content, {
            u'status': u'ok',
            u'message': u'Question is now First quiz',
        })
        lobby = active_lobby.get()
        self.assertEqual(lobby.pk, lobby_pk)
        self.assertIsNotNone(lobby.active_quiz)
        self.assertFalse(lobby.can_start)
        self.assertEqual(lobby.active_quiz.body.caption, 'First quiz')

        res = c.post(url, {'command': 'next'})
        self.assertJSONEqual(res.content, {
            u'status': u'ok',
            u'message': u'Question is now Second quiz',
        })
        lobby = active_lobby.get()
        self.assertEqual(lobby.pk, lobby_pk)
        self.assertEqual(lobby.active_quiz.body.caption, 'Second quiz')


