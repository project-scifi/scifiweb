from django.conf.urls import url

from scifiweb.home import home
from scifiweb.robots import robots_dot_txt

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^robots\.txt$', robots_dot_txt, name='robots.txt')
]
