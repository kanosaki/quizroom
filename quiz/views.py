from django.shortcuts import render, get_object_or_404
from django.utils.safestring import mark_safe
import django.core.exceptions
from django.http import HttpResponse
from quiz.viewutils import signin_required

import utils

from quiz import models


def index(req):
    return quiz_now(req)


def quiz_now(req):
    return render(req, 'quiz/index.html', {'foo': 'bar'})


def submit_answer(req, quiz_id):
    quiz = get_object_or_404(models.Quiz, pk=quiz_id)
    try:
        uid = req.session['uid']
        user = models.User.objects.get(pk=uid)
    except (KeyError, django.core.exceptions.ObjectDoesNotExist):
        return HttpResponse('Unauthorized', status=401)
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


def about_me(req):
    uid = req.session['uid']
    return uid
