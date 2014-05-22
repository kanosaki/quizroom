from django.db import models


class Quiz(models.Model):
    pass


class User(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return 'User %s' % self.name


class Answer(models.Model):
    quiz = models.ForeignKey(Quiz)
    selection = models.CharField(max_length=50)
    user = models.ForeignKey(User)

    def __str__(self):
        return 'Ans %s' % self.selection

