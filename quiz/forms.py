
from django import forms

from quiz.models import User, Quiz


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('name',)


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ('question',)
