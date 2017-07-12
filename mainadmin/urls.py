from django.conf.urls import url
from mainadmin.views import *

urlpatterns = [
    url(r'^admin_index.html$', index),
    url(r'^edit_article_(?P<category_id>\d+)_(?P<tag_id>\d+).html$', edit_article, name='article'),
    url(r'^add_article.html$', add_article),
    url(r'^edit_category.html$', edit_category),
    url(r'^edit_tag.html$', edit_tag),
    url(r'^edit_base_info.html$', edit_base_info),
    url(r'^upload_avatar.html$', upload_avatar),
    url(r'^update_tag(?P<nid>\d+).html$', update_tag),
    url(r'^update_category(?P<nid>\d+).html$', update_category),
    url(r'^update_article(?P<nid>\d+).html$', update_article),
]
