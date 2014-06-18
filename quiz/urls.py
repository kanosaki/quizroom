from django.conf.urls import patterns, include, url
from django.contrib import admin

from quiz import views
from quiz import viewmodels

admin.autodiscover()

participant_urls = patterns(
    '',
    url(r'^register$', viewmodels.CreateParticipant.as_view(), name='participant_register'),
    url(r'^signup$', viewmodels.CreateParticipant.as_view(), name='user_signup'),
)

lobby_urls = patterns(
    '',
    url(r'^now$', viewmodels.ActiveLobbyView.as_view(), name='lobby_now'),
    url(r'^(?P<pk>\d+)$', viewmodels.ViewLobby.as_view(), name='lobby_show'),
    url(r'^control/(?P<pk>\d+)$', viewmodels.ControlLobby.as_view(), name='lobby_control'),
    url(r'^ranking/now$', viewmodels.ViewLobbyRankingNow.as_view(), name='lobby_ranking_now'),
    url(r'^ranking/(?P<pk>\d+)$', viewmodels.ViewLobbyRanking.as_view(), name='lobby_ranking'),
)

urlpatterns = patterns(
    '',
    url(r'^user/', include(participant_urls)),
    url(r'^lobby/', include(lobby_urls)),
    url(r'^control/', views.game_control, name='game_control'),
    url(r'^mypage$', views.mypage, name='mypage'),
    url(r'^$', views.mypage, name='index'),
    url(r'^test$', views.unittest, name='test'),
)
