# -*- coding: utf-8 -*-

from collections import defaultdict

from django.db import models
from django.utils import timezone
import django.contrib.auth
from django.template.loader import render_to_string


class KVS(models.Model):
    key = models.CharField(primary_key=True, max_length=100)
    value = models.CharField(max_length=1000)

    @staticmethod
    def get(key):
        try:
            return KVS.objects.get(pk=key).value
        except KVS.DoesNotExist:
            raise KeyError(key)


    @staticmethod
    def put(key, value):
        entry = KVS(key=key, value=value)
        entry.save()


class Quiz(models.Model):
    caption = models.CharField(
        max_length=200,
        help_text=u'問題一覧等に表示される短い問題説明',
    )
    content = models.CharField(
        max_length=1000,
        help_text=u"問題文本体．'<','http://','https://'で始まる文字列の時，文字列をそのままレンダリングします"
                  u"それ以外の場合は問題文ディレクトリよりファイルを探索し，見つかったファイルをレンダリングします",
    )

    def get_content(self):
        if len(self.content) == 0 or self.content[0] == '<':
            return self.content
        else:
            return render_to_string(self.content)

    def get_choice(self, choice_index):
        choices = self.answerchoice_set.all()
        if choice_index > choices.count():
            raise Exception('There is no such choice')
        return choices[choice_index - 1]

    def get_score(self, choice_index):
        return self.get_choice(choice_index).base_score

    def __str__(self):
        return u'Quiz %d(%s)' % (self.id, self.caption)


class AnswerChoice(models.Model):
    quiz = models.ForeignKey(Quiz)

    base_score = models.IntegerField(
        help_text=u"基本的に正解は1，不正解は0とするが，ニアピン正解のようなものを作りたいときは正解10, ニアピン3, 不正解0の用に"
                  u"重みをつけて登録する．実際にどのようにスコアとして採用されるかは，QuizEntryやQuizSeriesに依存する",
    )
    content = models.CharField(
        max_length=1000,
        help_text=u"解答選択肢．'<','http://','https://'で始まる文字列の時，文字列をそのままレンダリングします"
                  u"それ以外の場合は問題文ディレクトリよりファイルを探索し，見つかったファイルをレンダリングします",
    )

    def get_content(self):
        if len(self.content) == 0 or self.content[0] == '<':
            return self.content
        else:
            return render_to_string(self.content)

    def __str__(self):
        return u'Answer for Quiz "%s" score %d' % (self.quiz.caption, self.base_score)


class QuizEntry(models.Model):
    body = models.ForeignKey(Quiz)

    order = models.IntegerField(help_text=u"何問目かを表す")

    opened_at = models.DateTimeField(
        null=True, blank=True,
        help_text=u"問題の表示=解答の受付が開始された時刻",
    )

    closed_at = models.DateTimeField(
        null=True, blank=True,
        help_text=u"出題の終了=解答の〆切が行われた時刻",
    )

    score_ratio = models.FloatField(
        default=1.0,
        help_text=u"最後の問題は配点100倍！！とかやりたいときのために",
    )

    @property
    def is_accepting(self):
        return self.closed_at is not None and self.closed_at < timezone.now()

    def reset(self):
        self.opened_at = None
        self.closed_at = None
        self.save()

    def open(self):
        self.opened_at = timezone.now()
        self.save()

    def close(self):
        self.closed_at = timezone.now()
        self.save()

    def get_score(self, choice_index):
        return self.body.get_score(choice_index)

    def __str__(self):
        return u'Quiz Series entry %d' % self.id


class QuizSeriesFinished(Exception):
    pass


class QuizSeries(models.Model):
    u"""実際にQuizをRoomで使用する時のためのデコレータ

    どのQuizを使って，どのようにユーザーのスコアを出して，どのように画面切り替えを行うか等の
    実際のゲーム進行のデータを制御します．
    """
    quizes = models.ManyToManyField(QuizEntry)
    active_quiz = models.ForeignKey(QuizEntry, blank=True, null=True, related_name='active_quiz')

    SCORING_TYPE = (
        ('CHOICE', 'Choice'),  # 正解・不正解制クイズ
        ('RATING', 'Rating'),  # ポイント(スコア)制クイズ
    )

    scoring_type = models.CharField(
        max_length=10,
        choices=SCORING_TYPE,
        help_text=u"Choiceにすると正解・不正解表示の問題になる．"
                  u"各問題では，選択肢のうち最もスコアの高いものが正解，それ以外が不正解として扱われる．"
                  u"Choiceでは最終的な正解の数によってユーザーのスコアが決定する"
                  u"Ratingでは，各問題のスコアがそのままスコアとして処理される．"
                  u"Ratingでは，スコアの積算が最終的なユーザーのスコアとなる．",
    )

    filp_interval_sec = models.FloatField(
        default=0.0,
        help_text=u"何秒で次の問題へ送るかを秒単位で指定します．0以下にすると自動で次の問題へ送りません",
    )

    def ordered_quiz(self):
        return self.quizes.order_by('order')

    def initialize(self):
        for quiz_entry in self.quizes.all():
            quiz_entry.reset()
        self.active_quiz = None
        self.save()

    def _load_first_quiz(self):
        first_quiz = self.ordered_quiz().first()
        self.active_quiz = first_quiz
        self.active_quiz.open()
        self.save()

    def _load_next_quiz(self):
        ordered_quizes = list(self.ordered_quiz())
        next_index = ordered_quizes.index(self.active_quiz) + 1
        self.active_quiz.close()
        if next_index <= len(ordered_quizes) - 1:
            self.active_quiz = ordered_quizes[next_index]
            self.active_quiz.open()
        else:
            self.active_quiz = None
        self.save()

    def go_next_quiz(self):
        if self.active_quiz is None:
            self._load_first_quiz()
        else:
            self._load_next_quiz()

    def __len__(self):
        return self.quizes.count()

    def __str__(self):
        return u'Quiz Series %d' % self.id


class Participant(models.Model):
    u"""基本的に，名前の登録のみで参加を可能にするため，セッションを使うが，Django側の認証システムを使って
    認証できるようにもしておく．また集計等もするかも(TODO)

    """
    name = models.CharField(max_length=30)
    session_key = models.CharField(max_length=128)
    django_user = models.ForeignKey(django.contrib.auth.get_user_model(), null=True, blank=True)

    def score_for(self, lobby):
        sum = 0
        for quiz_entry in lobby.quiz_series.quizes.all():
            try:
                ans = UserAnswer.objects.get(quiz=quiz_entry, user=self)
                sum += ans.score()
            except UserAnswer.DoesNotExist:
                pass
        return sum

    def __str__(self):
        return u'Participant %s' % self.name


class UserAnswer(models.Model):
    quiz = models.ForeignKey(QuizEntry)
    choice = models.IntegerField()
    user = models.ForeignKey(Participant)

    def __str__(self):
        return u'Ans %s' % self.choice

    def score(self):
        return self.quiz.get_score(self.choice)


class Lobby(models.Model):
    u"""クイズ全体の進行制御や，参加者の管理を行う"""

    # 基本的に
    # INACTIVE --(開始)--> QUIZ_OPENED --> MASTER_ANSWERING --> SHOWING_SCORE --(終了)--> CLOSED
    #                          ^                                     |
    #                          |<-----------(次の問題)-----------------
    #
    # という状態遷移．QUIZ_OPENED --> SHOWING_SCOREが主なループ
    STATES = (
        ('INACTIVE', 'Inactive'),  # 初期状態
        ('QUIZ_OPENED', 'Quiz Opened'),  # 問題を表示して，解答を受け付けている状態
        ('MASTER_ANSWERING', 'Master Answering'),  # 親が回答中
        ('SHOWING_ANSWER', 'Showing answer'),  # 親の解答が終了し，解答を受け付けている
        ('SHOWING_SCORE', 'Showing score'),  # 親の解答が終了し，解答を受け付けている
        ('CLOSED', 'Closed'),  # すべての問題が終了し，Lobbyが閉じている状態
    )
    PROPOSED_COMMANDS = {
        'INACTIVE': 'start_quiz',
        'QUIZ_OPENED': 'close_submission',
        'MASTER_ANSWERING': 'close_master_submission',
        'SHOWING_ANSWER': 'show_scores',
        'SHOWING_SCORE': 'next',
        'CLOSED': None,
    }

    @property
    def proposed_command(self):
        return self.PROPOSED_COMMANDS[self.current_state]

    quiz_series = models.ForeignKey(QuizSeries)
    players = models.ManyToManyField(Participant, null=True, blank=True)
    started_time = models.DateTimeField(null=True, blank=True)
    finished_time = models.DateTimeField(null=True, blank=True)
    current_state = models.CharField(
        max_length=30,
        choices=STATES,
        null=True, blank=True
    )

    def __str__(self):
        return u'Lobby %d' % self.id

    @property
    def status(self):
        return self.get_current_state_display()

    def initialize(self, force=False):
        self.quiz_series.initialize()
        self.started_time = timezone.now()
        self.finished_time = None
        self.current_state = 'INACTIVE'
        self.save()

    def close_participant_submission(self):
        self.current_state = 'MASTER_ANSWERING'
        self.save()

    def close_master_submission(self):
        self.current_state = 'SHOWING_ANSWER'
        self.save()

    def show_scores(self):
        self.current_state = 'SHOWING_SCORE'
        self.save()

    def open_quiz(self):
        self.current_state = 'QUIZ_OPENED'
        if self.active_quiz is None:
            self.go_next_quiz()
        if self.active_quiz is not None:
            self.active_quiz.open()
        self.save()

    def go_next_quiz(self):
        self.quiz_series.go_next_quiz()
        if self.active_quiz is None:
            self.finished_time = timezone.now()  # finished
            self.current_state = 'CLOSED'
        else:
            self.current_state = 'QUIZ_OPENED'
        self.save()

    @property
    def is_finished(self):
        return self.finished_time is not None

    @property
    def active_quiz(self):
        return self.quiz_series.active_quiz

    def quizes(self):
        for index, quiz in enumerate(self.quiz_series.ordered_quiz()):
            yield {
                'index': str(index),
                'caption': quiz.body.caption,
                'opened_at': quiz.opened_at,
                'closed_at': quiz.closed_at,
                'is_active': quiz == self.active_quiz,
            }

    def participants(self):
        for p in self.players.all():
            yield {
                'name': p.name,
            }

    def check_participant(self, participant):
        if self.players.filter(pk=participant.pk).count() == 0:
            self.players.add(participant)
            self.save()

    def _fetch_scores(self):
        for participant in self.players.all():
            yield (participant.score_for(self), participant)

    @property
    def score_list(self):
        """(スコア, Participant)のタプルのリストを返します

        リストはスコアの降順でソートされています
        :Example:
            [(10, <Participant Taro>), (5, <Participant Jiro>), (3, <Participant Saburo>)]
        """
        result = []
        prev_score = None
        rank = 1
        for (score, participant) in reversed(sorted(self._fetch_scores())):
            if prev_score is not None and score < prev_score:
                rank += 1
            result.append({
                'score': score,
                'name': participant.name,
                'participant_id': participant.id,
                'rank': rank,
            })
            prev_score = score
        return result

    def _fetch_all_answers(self):
        user_answers = UserAnswer.objects.get(quiz=self.active_quiz)
        for ans in user_answers:
            return {
                'name': ans.user.name,
                'participant_id': ans.user.id,
                'choice_id': ans.choice,
            }

    def all_answers(self):
        return list(self._fetch_all_answers())

    def answer_summary(self, requester_uid=None):
        choice_map = defaultdict(set)
        try:
            answers = list(UserAnswer.objects.filter(quiz=self.active_quiz))
        except UserAnswer.DoesNotExist:
            return {}
        for ans in answers:
            choice_map[ans.choice].add(ans)
        ret = []
        for (choice, answerers) in sorted(choice_map.items()):
            anses = [{'name': ans.user.name,
                      'participant_id': ans.user.id,
                      'is_you': ans.user.pk == requester_uid}
                     for ans in answerers]
            ret.append({
                'choice_id': choice + 1,
                'answerers': anses,
            })
        return ret

    def can_accept_answer(self, participant):
        return self.current_state == 'QUIZ_OPENED'  # TODO: Add master exception

    def submit_answer(self, participant, choice_id):
        active_quiz = self.active_quiz
        try:
            previous_ans = UserAnswer.objects.get(user=participant, quiz=active_quiz)
            previous_ans.choice = choice_id
            previous_ans.save()
        except UserAnswer.DoesNotExist:
            ans = UserAnswer(
                quiz=self.active_quiz,
                choice=int(choice_id),
                user=participant,
            )
            ans.save()




