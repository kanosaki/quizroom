from django.db import models

import django.contrib.auth


class Quiz(models.Model):
    caption = models.CharField(max_length=200)
    question = models.CharField(max_length=1000)

    def __str__(self):
        return 'Quiz %d(%s)' % (self.id, self.caption)


class QuizSeriesEntry(models.Model):
    body = models.ForeignKey(Quiz)
    order = models.IntegerField()

    def __str__(self):
        return 'Quiz Series entry %d' % self.id


class QuizSeries(models.Model):
    quizes = models.ManyToManyField(Quiz)

    def __str__(self):
        return 'Quiz Series %d' % self.id


class Participant(models.Model):
    name = models.CharField(max_length=30)
    session_key = models.CharField(max_length=128)
    django_user = models.ForeignKey(django.contrib.auth.get_user_model(), null=True, blank=True)

    def __str__(self):
        return 'Participant %s' % self.name


class Robby(models.Model):
    quiz_series = models.ForeignKey(QuizSeries)
    players = models.ManyToManyField(Participant)
    active_quiz = models.ForeignKey(Quiz, null=True, blank=True)
    started_time = models.DateTimeField(null=True, blank=True)
    finished_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return 'Robby %d' % self.id


class UserAnswer(models.Model):
    quiz = models.ForeignKey(Quiz)
    room = models.ForeignKey(Robby)
    selection = models.CharField(max_length=50)
    user = models.ForeignKey(Participant)

    def __str__(self):
        return 'Ans %s' % self.selection

    class Meta:
        unique_together = (('quiz', 'room'), )



