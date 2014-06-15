from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView  # , DeleteView
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView
from django.shortcuts import redirect, render

from quiz.forms import ParticipantForm, QuizForm
from quiz.models import Participant, Quiz, Lobby, UserAnswer
from quiz import control
import quizhub.lobby
import utils
from utils import api_guard



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

        if lobby.active_quiz is None:
            kw['quiz'] = None
            kw['choices'] = None
        else:
            quiz_body = lobby.active_quiz.body
            kw['quiz'] = quiz_body
            kw['choices'] = quiz_body.answerchoice_set.all()
        kw.update(
            participant=participant,
            lobby=lobby,
        )
        return kw

    def get(self, request, *args, **kwargs):
        try:
            context = self.get_context_data(
                lobby_id=kwargs['pk']
            )
            participant = context['participant']
            lobby = context['lobby']
            if lobby.players.filter(pk=participant.pk).count() == 0:
                lobby.join(participant)

            return self.render_to_response(context)
        except Participant.DoesNotExist:
            return redirect('participant_register')

    def post(self, request, *args, **kw):
        command = request.POST.get('command')
        if command == 'submit_answer':
            lobby_id = request.POST['lobby_id']
            context = self.get_context_data(lobby_id=lobby_id)
            active_quiz = context['lobby'].active_quiz
            if not active_quiz.is_accepting:
                return utils.JsonStatuses.failed('Closed')
            if 'choice_id' not in request.POST:
                return utils.JsonStatuses.failed('Invalid POST: choice_id required.')
            choice_id = request.POST['choice_id']
            ans = UserAnswer(
                quiz=active_quiz,
                choice=int(choice_id),
                user=context['participant'],
            )
            ans.save()
            return utils.JsonStatuses.ok()
        else:
            return utils.JsonStatuses.failed('Unknown command')


class ControlLobby(TemplateView):
    template_name = 'quiz/lobby/control.html'

    def get(self, req, *args, **kw):
        lobby = Lobby.objects.get(pk=kw['pk'])
        return render(req, self.template_name, {
            'lobby': lobby,
        })

    @api_guard
    def post(self, req, *args, **kw):
        lobby = Lobby.objects.get(pk=kw['pk'])
        command = req.POST['command']
        if command == 'activate':
            lobby.initialize(force=True)
        elif command == 'start_quiz':
            lobby.go_next_quiz()
        elif command == 'close_submission':
            lobby.close_participant_submission()
        elif command == 'show_scores':
            lobby.close_master_submission()
        elif command == 'next':
            lobby.go_next_quiz()
            if lobby.is_finished:
                return utils.JsonStatuses.failed('Already closed!')
        else:
            return utils.JsonStatuses.failed('Unknown command!')
        quizhub.lobby.lobby_hub.request_update()
        return utils.JsonStatuses.ok()


class ActiveLobbyView(TemplateView):
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
        control.active_lobby.set(lobby)
        return utils.JsonStatuses.ok(message='Active lobby set to Lobby %d' % lobby.pk)


