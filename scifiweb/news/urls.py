from django.conf.urls import url

import scifiweb.news.views as views


urlpatterns = [
    # Simulate stock WordPress routing rules
    url(r'^$', views.render_search, name='news'),
    url(r'^(\d{4})/(\d{2})/(\d{2})/([^/]+)/$', views.render_post_by_ymds,
        name='post'),
    url(r'^(\d{4})/(\d{2})/(\d{2})/$', views.redirect_search_by_ymd),
    url(r'^(\d{4})/(\d{2})/([^/]+)/$', views.redirect_post_by_yms),
    url(r'^(\d{4})/(\d{2})/$', views.redirect_search_by_ym),
    url(r'^(\d{4})/$', views.redirect_search_by_year),
    url(r'^archives/(\d*)/$', views.redirect_post_by_id),
    url(r'^(.+)/$', views.redirect_post_by_slug),
]
