from django.conf.urls import patterns, include, url
from django.contrib import admin

from quiz import views
from quiz import viewmodels

admin.autodiscover()

user_urls = patterns(
    '',
    url(r'^Update$', viewmodels.UpdateUser.as_view(), name='user_update'),
    url(r'^signup_auto$', views.signup_user, name='user_signup_auto'),
    url(r'^signup$', viewmodels.CreateUser.as_view(), name='user_signup'),
    url(r'^list$', viewmodels.UserList.as_view(), name='user_list'),
    url(r'^(?P<pk>\d+)/', viewmodels.ViewUser.as_view(), name='user_view'),
)

quiz_urls = patterns(
    '',
    url(r'^list$', viewmodels.ListQuiz.as_view(), name='quiz_list'),
    url(r'^(?P<pk>\d+)/$', viewmodels.ViewQuiz.as_view(), name='quiz_view'),
    url(r'^(?P<pk>\d+)/submit_answer', views.submit_answer, name='quiz_submit_answer'),
)

playquiz_urls = patterns(
    '',
    url(r'^now$', views.quiz_now, name='playquiz_now'),
)

urlpatterns = patterns(
    '',
    url(r'^quiz/', include(quiz_urls)),
    url(r'^user/', include(user_urls)),
    url(r'^play/', include(playquiz_urls)),
    url(r'^my$', views.about_me, name='user_me'),
    url(r'^$', views.about_me, name='user_me'),
)
