from django.conf.urls import include
from django.conf.urls import url

import scifiweb.info.urls
from scifiweb.home import home
from scifiweb.robots import robots_dot_txt

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^robots\.txt$', robots_dot_txt, name='robots.txt'),

    url(r'^info/', include(scifiweb.info.urls.urlpatterns)),
]
