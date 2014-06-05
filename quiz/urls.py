from django.conf.urls import patterns, include, url
from django.contrib import admin

from quiz import views
from quiz import viewmodels

admin.autodiscover()

participant_urls = patterns(
    '',
    url(r'^Update$', viewmodels.UpdateParticipant.as_view(), name='participant_update'),
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

lobby_urls = patterns(
    '',
    url(r'^now$', viewmodels.ActiveLobbyView.as_view(), name='lobby_now'),
    url(r'^(?P<pk>\d+)/$', viewmodels.ViewLobby.as_view(), name='lobby_show'),
    url(r'^control/(?P<pk>\d+)/$', viewmodels.ControlLobby.as_view(), name='lobby_control'),
)

urlpatterns = patterns(
    '',
    url(r'^quiz/', include(quiz_urls)),
    url(r'^user/', include(participant_urls)),
    url(r'^lobby/', include(lobby_urls)),
    url(r'^control/', views.game_control, name='game_control'),
    url(r'^mypage$', views.mypage, name='mypage'),
    url(r'^$', views.mypage, name='index'),
)
