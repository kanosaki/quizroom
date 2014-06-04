from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView  # , DeleteView
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse_lazy

from quiz.forms import ParticipantForm, QuizForm
from quiz.models import Participant, Quiz, Lobby
import quiz.control


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
        session_key = request.session.session_key
        name = request.POST['name']
        part = Participant(name=name, session_key=session_key, django_user=None)
        part.save()
        request.session['name'] = name
        request.session['uid'] = part.id
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
        kw.update(participant=participant)
        return kw

    def get(self, request, *args, **kwargs):
        try:
            return self.render_to_response(self.get_context_data())
        except KeyError:
            return redirect('participant_register')


class ControlLobby(TemplateView):
    template_name = 'quiz/lobby/control.html'

    def get_context_data(self, **kw):
        return kw


class ActiveLobbyView(TemplateView):
    template_name = 'quiz/lobby/view.html'

    def get(self, request, *args, **kwargs):
        active_lobby = quiz.control.active_lobby.get()
        if active_lobby is not None:
            return redirect('lobby_show', active_lobby.pk)
        else:
            return render(request, 'quiz/lobby/nolobby.html')




