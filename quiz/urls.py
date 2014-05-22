from django.conf.urls import patterns, include, url
from django.contrib import admin

from quiz import views

urlpatterns = patterns(
    '',
    url(r'(?P<quiz_id>\d+)/submit_answer', views.submit_answer, name='submit_answer'),
    url(r'signup_user', views.signup_user, name='signup_user'),
)
