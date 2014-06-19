from django.shortcuts import render, get_object_or_404
import django.core.exceptions
from django.http import HttpResponse, HttpResponseNotFound
from django.conf import settings
from django.contrib.auth.decorators import login_required

import utils
from quiz.models import Lobby, Quiz, Participant, UserAnswer
from quiz.viewutils import signin_required


def index(req):
    return quiz_now(req)


def quiz_now(req):
    return render(req, 'quiz/index.html', {'foo': 'bar'})


def submit_answer(req, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    try:
        uid = req.session['uid']
        user = Participant.objects.get(pk=uid)
    except (KeyError, django.core.exceptions.ObjectDoesNotExist):
        return HttpResponse('Unauthorized', status=401)
    ans_selection = req.REQUEST['answer']
    ans = UserAnswer(quiz=quiz, selection=ans_selection, user=user)
    ans.save()
    return utils.JsonStatuses.OK

@login_required
def game_control(req):
    return render(req, 'quiz/game_control.html', {
        'lobbies': Lobby.objects.all(),
    })


@signin_required
def mypage(req, user):
    return render(req, 'quiz/mypage.html', {'user': user})


def unittest(req):
    if settings.DEBUG:
        return render(req, 'quiz/unittest.html')
    else:
        return HttpResponseNotFound()
