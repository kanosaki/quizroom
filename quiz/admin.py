from django.contrib import admin

import quiz.models


class UserAdmin(admin.ModelAdmin):
    pass

admin.site.register(quiz.models.User, UserAdmin)


class QuizAdmin(admin.ModelAdmin):
    pass
admin.site.register(quiz.models.Quiz, QuizAdmin)


class AnswerAdmin(admin.ModelAdmin):
    pass
admin.site.register(quiz.models.Answer, AnswerAdmin)
