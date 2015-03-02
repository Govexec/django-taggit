from django.conf.urls import patterns, url

from taggit import views

urlpatterns = patterns('',
	url(r'^static/(?P<path>.*)$', views.media, name='taggit-static'),
	url(r'^ajax$', views.ajax, name='taggit-ajax'),
)
