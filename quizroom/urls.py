from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import quiz.views

urlpatterns = patterns(
    '',
    url(r'^$', quiz.views.index, name="index"),
    url(r'^quiz/', include('quiz.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
