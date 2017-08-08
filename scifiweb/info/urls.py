from django.conf.urls import url

from scifiweb.info.article import get_articles
from scifiweb.info.article import INDEX


urlpatterns = (
    [
        url(r'^$', INDEX.renderer, name='info'),
    ] +
    [
        url(r'^{}/$'.format(article.name), article.renderer, name=article.url_name)
        for article in get_articles().values() if article.name
    ]
)
