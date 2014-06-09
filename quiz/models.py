# -*- coding: utf-8 -*-
from datetime import datetime
from django.db import models
import django.contrib.auth


class KVS(models.Model):
    key = models.CharField(primary_key=True, max_length=100)
    value = models.CharField(max_length=1000)

    @staticmethod
    def get(key):
        return KVS.objects.get(pk=key)

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

    def __unicode__(self):
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

    def __unicode__(self):
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

    def __unicode__(self):
        return u'Quiz Series entry %d' % self.id


class QuizSeriesFinished(Exception):
    pass


class QuizSeries(models.Model):
    u"""実際にQuizをRoomで使用する時のためのデコレータ

    どのQuizを使って，どのようにユーザーのスコアを出して，どのように画面切り替えを行うか等の
    実際のゲーム進行のデータを制御します
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

    def initialize_quizseries(self):
        first_quiz = self.ordered_quiz().first()
        self.active_quiz = first_quiz
        self.save()

    def go_next_quiz(self):
        ordered_quizes = list(self.ordered_quiz())
        next_index = ordered_quizes.index(self.active_quiz) + 1
        if next_index < len(ordered_quizes) - 1:
            self.active_quiz = ordered_quizes[next_index]
        else:
            self.active_quiz = None
        self.save()

    def __len__(self):
        return self.quizes.count()

    def __unicode__(self):
        return u'Quiz Series %d' % self.id


class Participant(models.Model):
    u"""基本的に，名前の登録のみで参加を可能にするため，セッションを使うが，Django側の認証システムを使って
    認証できるようにもしておく．また集計等もするかも(TODO)

    """
    name = models.CharField(max_length=30)
    session_key = models.CharField(max_length=128)
    django_user = models.ForeignKey(django.contrib.auth.get_user_model(), null=True, blank=True)

    def __unicode__(self):
        return u'Participant %s' % self.name


class UserAnswer(models.Model):
    quiz = models.ForeignKey(QuizEntry)
    choice = models.IntegerField()
    user = models.ForeignKey(Participant)

    def __unicode__(self):
        return u'Ans %s' % self.selection


class Lobby(models.Model):
    u"""クイズ全体の進行制御や，参加者の管理を行う"""
    quiz_series = models.ForeignKey(QuizSeries)
    players = models.ManyToManyField(Participant, null=True, blank=True)
    started_time = models.DateTimeField(null=True, blank=True)
    finished_time = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return u'Lobby %d' % self.id

    @property
    def status(self):
        if self.active_quiz is None:
            if self.started_time is None:
                return u'Ready'
            else:
                return u'Closed'
        else:
            return u'Active'

    @property
    def can_start(self):
        return len(self.quiz_series) > 0 and \
               self.active_quiz is None and \
               self.started_time is None

    def start(self, force=False):
        if self.can_start or force:
            self.quiz_series.initialize_quizseries()
            self.started_time = datetime.now()
            self.save()
        else:
            raise RuntimeError('Cannot open')

    def go_next_quiz(self):
        self.quiz_series.go_next_quiz()
        if self.active_quiz is None:
            self.finished_time = datetime.now()  # finished

    @property
    def active_quiz(self):
        return self.quiz_series.active_quiz



