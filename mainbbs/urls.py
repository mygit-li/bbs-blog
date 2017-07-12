from django.conf.urls import url
from mainbbs.views import *

urlpatterns = [
    url(r'^bbs_index.html$', index),
    url(r'^all/(?P<article_type_id>\d+).html$', index, name='index'),
]
