from django.db import models


class Quiz(models.Model):
    caption = models.CharField(max_length=200)
    question = models.CharField(max_length=1000)


class QuizSeriesEntry(models.Model):
    body = models.ForeignKey(Quiz)
    order = models.IntegerField()


class QuizSeries(models.Model):
    quizes = models.ManyToManyField(Quiz)


class User(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return 'User %s' % self.name


class Room(models.Model):
    quiz_series = models.ForeignKey(QuizSeries)
    players = models.ManyToManyField(User)
    active_quiz = models.ForeignKey(Quiz)


class UserAnswer(models.Model):
    quiz = models.ForeignKey(Quiz)
    room = models.ForeignKey(Room)
    selection = models.CharField(max_length=50)
    user = models.ForeignKey(User)

    def __str__(self):
        return 'Ans %s' % self.selection



