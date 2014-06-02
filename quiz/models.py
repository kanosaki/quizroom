from django.db import models

import django.contrib.auth


class Quiz(models.Model):
    caption = models.CharField(max_length=200)
    question = models.CharField(max_length=1000)


class QuizSeriesEntry(models.Model):
    body = models.ForeignKey(Quiz)
    order = models.IntegerField()


class QuizSeries(models.Model):
    quizes = models.ManyToManyField(Quiz)


class Participant(models.Model):
    name = models.CharField(max_length=30)
    session_key = models.CharField(max_length=128)
    django_user = models.ForeignKey(django.contrib.auth.get_user_model(), null=True)

    def __str__(self):
        return 'Participant %s' % self.name


class Room(models.Model):
    quiz_series = models.ForeignKey(QuizSeries)
    players = models.ManyToManyField(Participant)
    active_quiz = models.ForeignKey(Quiz)
    started_time = models.DateTimeField(null=True)
    finished_time = models.DateTimeField(null=True)


class UserAnswer(models.Model):
    quiz = models.ForeignKey(Quiz)
    room = models.ForeignKey(Room)
    selection = models.CharField(max_length=50)
    user = models.ForeignKey(Participant)

    def __str__(self):
        return 'Ans %s' % self.selection

    class Meta:
        unique_together = (('quiz', 'room'), )



