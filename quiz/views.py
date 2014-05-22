from django.shortcuts import render

import utils

from quiz import models


def index(req):
    return current(req)


def current(req):
    return render(req, 'quiz/index.html', {'foo': 'bar'})


def submit_answer(req, quiz_id):
    quiz = models.Quiz.objects.get(pk=quiz_id)
    uid = req.session['uid']
    user = models.User.objects.get(pk=uid)
    ans_selection = req.REQUEST['answer']
    ans = models.Answer(quiz=quiz, selection=ans_selection, user=user)
    ans.save()
    return utils.JsonStatuses.OK


def signup_user(req):
    name = req.REQUEST['name']
    user = models.User(name=name)
    user.save()
    req.session['uid'] = user.pk
    req.session['name'] = name
    return utils.JsonStatuses.OK



