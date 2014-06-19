# -*- coding: utf-8 -*-
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView  # , DeleteView
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, render, get_object_or_404
from django.core.exceptions import PermissionDenied

from quiz.forms import ParticipantForm, QuizForm
from quiz.models import Participant, Quiz, Lobby
from quiz import control
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
        lobby.check_participant(participant)

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

    def get_score_list(self, uid):
        lobby = Lobby.objects.get(pk=self.kwargs['pk'])
        request_participant = Participant.objects.get(pk=uid)
        score_list = lobby.score_list

        def append_is_you_filter(entry):
            """スコアの要素を走査し，そのスコアがリクエストした人だった場合は is_you: True を足して
            そうで無ければ is_you: False を追加します
            """
            if entry['participant_id'] == request_participant.id:
                entry['is_you'] = True
            else:
                entry['is_you'] = False
            return entry

        return [append_is_you_filter(entry) for entry in score_list]

    def get_all_answers(self):
        lobby = Lobby.objects.get(pk=self.kwargs['pk'])
        return lobby.all_answers()

    def get_answer_summary(self):
        lobby = Lobby.objects.get(pk=self.kwargs['pk'])
        return lobby.answer_summary(
            self.request.session.get('uid')
        )

    def query_data(self, request, *args, **kw):
        command = request.GET.get('command')
        if command == 'score_list':
            uid = request.session['uid']
            return utils.JsonStatuses.ok(content=self.get_score_list(uid))
        elif command == 'all_answers':
            return utils.JsonStatuses.ok(content=self.get_all_answers())
        elif command == 'answer_summary':
            return utils.JsonStatuses.ok(content=self.get_answer_summary())
        else:
            return utils.JsonStatuses.failed('Unknown command %s' % command)

    def get(self, request, *args, **kwargs):
        """GET

        クエリが無い場合は，quiz/lobby/view.htmlを用いてHTMLを返します
        ユーザーが登録していない場合は，登録ページへリダイレクトします

        クエリパラメータ?type=query があるときは，JSONを返します
        * ?type=query&command=score_list
            各参加者とそのスコアのリストを返します．
            返されるJSONは，スコアで降順ソートされており，
            同様にランキングで昇順ソートされています．このとき，スコアが同じ場合はランキングが変化しません．
            例:
                {'status': 'ok',
                 'content':
                    [{'score': 1,
                      'rank': 1,
                      'name': 'test_user1',
                      'participant_id': 1,
                      'is_you': True},
                     ....
                     ]}
            それぞれ
                score: 参加者の得点 :: 数値(たぶん整数値)
                rank: 参加者の順位(同率あり) :: 整数値
                name: 名前(文字列)
                participant_id: 内部で用いる参加者ID
                is_you: このリクエストを送った人のスコアの時True, そうでなければFalse
        * ?type=query&command=all_answers
            参加者の回答一覧を返します
            {'status': 'ok',
             'content': [
                {'name': 'test_user', 'participant_id': 1, 'choice_id': 1},
                ....
             ]}
        * ?type=query&command=answer_summary
            この問題の，それぞれの選択肢に何票入ったかを集計します
            {'status': 'ok',
             'content': [
                {'choice_id': 1,
                 'answerers': [
                    {'name': 'test_user', 'participant_id': 1},
                    ...
                 ],
                 ...
             ]}
        """
        try:
            if request.GET.get('type') == 'query':
                return self.query_data(request, *args, **kwargs)
            context = self.get_context_data(
                lobby_id=kwargs['pk']
            )
            return self.render_to_response(context)
        except Participant.DoesNotExist:
            return redirect('participant_register')

    def post(self, request, *args, **kw):
        command = request.POST.get('command')
        if command == 'submit_answer':
            lobby_id = request.POST['lobby_id']
            context = self.get_context_data(lobby_id=lobby_id)
            lobby = context['lobby']
            participant = context['participant']
            if 'choice_id' not in request.POST:
                return utils.JsonStatuses.failed('Invalid POST: choice_id required.')
            choice_id = request.POST['choice_id']
            if request.user.is_authenticated():
                if lobby.current_state == 'MASTER_ANSWERING':
                    lobby.submit_master_answer(choice_id)
                else:
                    return utils.JsonStatuses.failed('現在は回答できません')
            else:
                if lobby.current_state == 'QUIZ_OPENED':
                    lobby.submit_answer(participant, choice_id)
                else:
                    return utils.JsonStatuses.failed('現在は回答できません')
            return utils.JsonStatuses.ok()
        else:
            return utils.JsonStatuses.failed('Unknown command')


class ViewLobbyRanking(TemplateView):
    template_name = 'quiz/score/view.html'

    def get_context_data(self, **kwargs):
        lobby_id = kwargs.get('pk')
        lobby = get_object_or_404(Lobby, pk=lobby_id)
        return {
            'quiz': lobby.active_quiz,
            'lobby': lobby,
        }


class ViewLobbyRankingNow(TemplateView):
    def get(self, request, *args, **kwargs):
        active_lobby = control.active_lobby.get()
        if active_lobby is not None:
            return redirect('lobby_ranking', active_lobby.pk)
        else:
            return render(request, 'quiz/lobby/nolobby.html')


class ControlLobby(TemplateView):
    template_name = 'quiz/lobby/control.html'

    @method_decorator(login_required(login_url='/admin'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

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
            lobby.open_quiz()
        elif command == 'close_submission':
            lobby.close_participant_submission()
        elif command == 'close_master_submission':
            lobby.close_master_submission()
        elif command == 'show_scores':
            lobby.show_scores()
        elif command == 'next':
            lobby.go_next_quiz()
            if lobby.is_finished:
                return utils.JsonStatuses.failed('Already closed!')
        else:
            return utils.JsonStatuses.failed('Unknown command!')
        return utils.JsonStatuses.ok()


class ViewLobbyPresenter(TemplateView):
    template_name = 'quiz/presenter/view.html'

    def get_context_data(self, **kw):
        lobby_id = self.kwargs.get('pk')
        lobby = get_object_or_404(Lobby, pk=lobby_id)
        active_quiz = lobby.active_quiz
        if active_quiz is not None:
            quiz_body = active_quiz.body
            choices = list(active_quiz.choices)
        else:
            choices = []
            quiz_body = None
        kw.update({
            'lobby': lobby,
            'quiz': quiz_body,
            'choices': choices,
        })
        return kw


class ActiveLobbyView(TemplateView):
    template_name = 'quiz/lobby/view.html'

    def get(self, request, *args, **kwargs):
        active_lobby = control.active_lobby.get()
        if active_lobby is not None:
            return redirect('lobby_show', active_lobby.pk)
        else:
            return render(request, 'quiz/lobby/nolobby.html')

    def post(self, req, *args, **kw):
        if not req.user.is_authenticated():
            raise PermissionDenied()
        activating_id = req.POST['id']
        if activating_id == 'default':
            lobby = Lobby.objects.filter(started_time=None).first()
        else:
            lobby = Lobby.objects.get(pk=activating_id)
        control.active_lobby.set(lobby)
        return utils.JsonStatuses.ok(message='Active lobby set to Lobby %d' % lobby.pk)


