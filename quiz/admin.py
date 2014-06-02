from django.contrib import admin

import quiz.models


class ParticipantAdmin(admin.ModelAdmin):
    pass

admin.site.register(quiz.models.Participant, ParticipantAdmin)


class QuizAdmin(admin.ModelAdmin):
    pass
admin.site.register(quiz.models.Quiz, QuizAdmin)


class RoomAdmin(admin.ModelAdmin):
    pass
admin.site.register(quiz.models.Robby, RoomAdmin)


class QuizSeriesAdmin(admin.ModelAdmin):
    pass
admin.site.register(quiz.models.QuizSeries, QuizSeriesAdmin)


class UserAnswerAdmin(admin.ModelAdmin):
    pass
admin.site.register(quiz.models.UserAnswer, UserAnswerAdmin)
