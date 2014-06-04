# -*- coding: utf-8 -*-

from django.db import models
import django.contrib.auth


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


class QuizSeries(models.Model):
    u"""実際にQuizをRoomで使用する時のためのデコレータ

    どのQuizを使って，どのようにユーザーのスコアを出して，どのように画面切り替えを行うか等の
    実際のゲーム進行のデータを制御します
    """
    quizes = models.ManyToManyField(QuizEntry)

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
    active_quiz = models.ForeignKey(Quiz, null=True, blank=True)
    started_time = models.DateTimeField(null=True, blank=True)
    finished_time = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return u'Lobby %d' % self.id


