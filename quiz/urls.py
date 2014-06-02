from django.conf.urls import patterns, include, url
from django.contrib import admin

from quiz import views
from quiz import viewmodels

admin.autodiscover()

participant_urls = patterns(
    '',
    url(r'^Update$', viewmodels.UpdateParticipant.as_view(), name='participant_update'),
    url(r'^signup_auto$', views.signup_user, name='participant_signup_auto'),
    url(r'^register$', viewmodels.CreateParticipant.as_view(), name='participant_register'),
    url(r'^list$', viewmodels.UserList.as_view(), name='participant_list'),
    url(r'^(?P<pk>\d+)/', viewmodels.ViewUser.as_view(), name='participant_view'),
    url(r'^signup$', viewmodels.CreateParticipant.as_view(), name='user_signup'),
)

quiz_urls = patterns(
    '',
    url(r'^list$', viewmodels.ListQuiz.as_view(), name='quiz_list'),
    url(r'^(?P<pk>\d+)/$', viewmodels.ViewQuiz.as_view(), name='quiz_view'),
    url(r'^(?P<pk>\d+)/submit_answer', views.submit_answer, name='quiz_submit_answer'),
)

playquiz_urls = patterns(
    '',
    url(r'^now$', viewmodels.RoomNowView.as_view(), name='play_now'),
)

urlpatterns = patterns(
    '',
    url(r'^quiz/', include(quiz_urls)),
    url(r'^user/', include(participant_urls)),
    url(r'^play/', include(playquiz_urls)),
    url(r'^mypage$', views.mypage, name='mypage'),
)
