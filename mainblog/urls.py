from django.conf.urls import url
from mainblog.views import *

urlpatterns = [
    url(r'^blog_(?P<site>\w+).html$', index),
    url(r'^(?P<site>\w+)/(?P<article_id>\d+).html$', article_detail),
    url(r'^(?P<site>\w+)/(?P<condition>((tag)|(date)|(category)))/(?P<val>\w+-*\w*).html$', article_filter),

]
