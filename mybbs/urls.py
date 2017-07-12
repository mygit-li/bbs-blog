"""mybbs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from mybbs.views import login, register, check_code, logout

urlpatterns = [
    url(r'^$', login),
    url(r'^login/$', login),
    url(r'^register/$', register),
    url(r'^logout/$', logout),
    url(r'^check_code/$', check_code),
    url(r'^mainadmin/', include('mainadmin.urls')),
    url(r'^mainblog/', include('mainblog.urls')),
    url(r'^mainbbs/', include('mainbbs.urls')),
]
