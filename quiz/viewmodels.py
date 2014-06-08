from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView  # , DeleteView
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView, View
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse_lazy

from quiz.forms import ParticipantForm, QuizForm
from quiz.models import Participant, Quiz, Lobby
from utils import JsonResponse
from quiz import control


# ----------------------------------
# User
# ----------------------------------
class ParticipantMixin(object):
    model = Participant

    def get_context_data(self, **kw):
        kw.update({'object_name': 'Participant'})
        return kw


class ParticipantFormMixin(ParticipantMixin):
    formclass = ParticipantForm
    template_name = 'quiz/participants/form.html'


class UserList(ParticipantMixin, ListView):
    template_name = 'quiz/participants/list.html'


class ViewUser(ParticipantMixin, DetailView):
    pass


class CreateParticipant(ParticipantFormMixin, CreateView):
    template_name = 'quiz/participants/register.html'

    def post(self, request, *args, **kwargs):
        name = request.POST['name']
        if not request.session.exists(request.session.session_key):
            request.session.create()
        session_key = request.session.session_key
        part = Participant(name=name, session_key=session_key, django_user=None)
        part.save()
        request.session['uid'] = part.id
        request.session['name'] = name
        return redirect('mypage')


class UpdateParticipant(ParticipantFormMixin, UpdateView):
    pass


# ----------------------------------
# Quiz
# ----------------------------------
class QuizMixin(object):
    model = Quiz

    def get_context_data(self, **kw):
        kw.update({'object_name': Quiz})
        return kw


class QuizFormMixin(QuizMixin):
    formclass = QuizForm
    template_name = 'quiz/quiz/form.html'


class ViewQuiz(QuizMixin, DetailView):
    template_name = 'quiz/quiz/view.html'


class ListQuiz(QuizMixin, ListView):
    template_name = 'quiz/quiz/list.html'

    def get_context_data(self, **kw):
        kw['quizes'] = Quiz.objects.all()
        return kw


class CreateQuiz(QuizFormMixin, CreateView):
    pass


class UpdateQuiz(QuizFormMixin, UpdateView):
    pass


class ViewLobby(TemplateView):
    template_name = 'quiz/lobby/view.html'

    def get_context_data(self, **kw):
        uid = self.request.session['uid']
        participant = Participant.objects.get(pk=uid)
        lobby = Lobby.objects.get(pk=kw['lobby_id'])

        quiz_body = lobby.active_quiz.body
        kw.update(
            participant=participant,
            lobby=lobby,
            quiz=quiz_body,
            choices=quiz_body.answerchoice_set.all(),
        )
        return kw

    def get(self, request, *args, **kwargs):
        try:
            return self.render_to_response(
                self.get_context_data(
                    lobby_id=kwargs['pk']
                )
            )
        except KeyError:
            return redirect('participant_register')


class ControlLobby(View):
    template_name = 'quiz/lobby/control.html'

    def get_context_data(self, **kw):
        return kw

    def get(self, req, *args, **kw):
        lobby = Lobby.objects.get(pk=kw['pk'])
        return render(req, self.template_name, {
            'lobby': lobby,
        })

    def post(self, req, *args, **kw):
        lobby = Lobby.objects.get(pk=kw['pk'])
        command = req.POST['command']
        if command == 'activate':
            lobby.start(force=True)
            control.active_lobby.set(lobby.pk)
        elif command == 'start':
            lobby.start_quiz()
        elif command == 'next':
            lobby.go_next_quiz()
        else:
            return JsonResponse({'status': 'Error', 'msg': 'Unknown command'})
        return JsonResponse({'status': 'OK'})


class ActiveLobbyView(View):
    template_name = 'quiz/lobby/view.html'

    def get(self, request, *args, **kwargs):
        active_lobby = control.active_lobby.get()
        if active_lobby is not None:
            return redirect('lobby_show', active_lobby.pk)
        else:
            return render(request, 'quiz/lobby/nolobby.html')

    def post(self, req, *args, **kw):
        activating_id = req.POST['id']
        if activating_id == 'default':
            lobby = Lobby.objects.filter(started_time=None).first()
        else:
            lobby = Lobby.objects.get(pk=activating_id)
        control.active_lobby.set(lobby.pk)
        return JsonResponse({'status': 'OK'})


