from django.contrib import admin

import quiz.models


class ParticipantAdmin(admin.ModelAdmin):
    pass

admin.site.register(quiz.models.Participant, ParticipantAdmin)
admin.site.register(quiz.models.Quiz)
admin.site.register(quiz.models.QuizEntry)
admin.site.register(quiz.models.AnswerChoice)
admin.site.register(quiz.models.Lobby)
admin.site.register(quiz.models.QuizSeries)
admin.site.register(quiz.models.UserAnswer)
