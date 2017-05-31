from django.conf.urls import url

from scifiweb.home import home

urlpatterns = [
    url(r'^$', home, name='home'),
]
