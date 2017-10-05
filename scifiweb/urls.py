from django.conf.urls import include
from django.conf.urls import url
from django.shortcuts import redirect
from django.shortcuts import reverse

import scifiweb.info.urls
import scifiweb.news.urls
from scifiweb.home import home
from scifiweb.robots import robots_dot_txt

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^robots\.txt$', robots_dot_txt, name='robots.txt'),

    url(r'^about/', include(scifiweb.info.urls.urlpatterns)),
    url(r'^news/', include(scifiweb.news.urls.urlpatterns)),

    # Legacy redirects to /about/
    url(r'^info/about/$', lambda _: redirect(reverse('about'), permanent=True)),
    url(r'^info/about/contact$', lambda _: redirect(reverse('about/contact'), permanent=True)),
    url(r'^info/about/team$', lambda _: redirect(reverse('about/team'), permanent=True)),
]
