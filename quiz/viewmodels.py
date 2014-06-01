from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView  # , DeleteView
from django.views.generic.detail import DetailView
from django.http import HttpRequest

from quiz.forms import UserForm, QuizForm
from quiz.models import User, Quiz


# ----------------------------------
# User
# ----------------------------------
class UserMixin(object):
    model = User

    def get_context_data(self, **kw):
        kw.update({'object_name': 'User'})
        return kw


class UserFormMixin(UserMixin):
    formclass = UserForm
    template_name = 'quiz/user/form.html'


class UserList(UserMixin, ListView):
    template_name = 'quiz/user/list.html'


class ViewUser(UserMixin, DetailView):
    pass


class CreateUser(UserFormMixin, CreateView):
    def post(self, request: HttpRequest, *args, **kwargs):
        super().post(request, *args, **kwargs)
        request.session['uid'] = self.object.id


class UpdateUser(UserFormMixin, UpdateView):
    pass


# ----------------------------------
# Quiz
# ----------------------------------
class QuizMixin(object):
    model = Quiz

    def get_context_data(self, **kw):
        kw.update({'object_name': Quiz})
        return kw


class QuizFormMixin(QuizMixin):
    formclass = QuizForm
    template_name = 'quiz/quiz/form.html'


class ViewQuiz(QuizMixin, DetailView):
    template_name = 'quiz/quiz/view.html'


class ListQuiz(QuizMixin, ListView):
    template_name = 'quiz/quiz/list.html'

    def get_context_data(self, **kw):
        kw['quizes'] = Quiz.objects.all()
        return kw

class CreateQuiz(QuizFormMixin, CreateView):
    pass


class UpdateQuiz(QuizFormMixin, UpdateView):
    pass

