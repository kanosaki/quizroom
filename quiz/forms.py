
from django import forms

from quiz.models import Participant, Quiz


class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ('name',)


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ('question',)

