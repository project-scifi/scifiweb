from itertools import chain

from django.conf.urls import url

import scifiweb.info.views as views
from scifiweb.info.article import Article
from scifiweb.info.article import article_tree
from scifiweb.info.article import article_view
from scifiweb.info.article import get_normal_articles


def get_articles():
    # This is a workaround for templatetags.article, which needs to import this
    # module while ARTICLES is being constructed
    return ARTICLES


def get_article_tree():
    # Likewise
    return ARTICLE_TREE


INDEX = Article('', 'Info', article_view('info/index.html'))

ARTICLES = {
    article.name: article
    for article in chain(
        get_normal_articles(),
        (
            INDEX,
            Article('about/team', 'Our team', views.team),
        ),
    )
}

ARTICLE_TREE = article_tree(ARTICLES.values())


urlpatterns = list(chain(
    (
        url(r'^$', INDEX.render, name='info'),
    ),
    (
        url(r'^{}/$'.format(article.name), article.render, name=article.url_name)
        for article in ARTICLES.values() if article.name
    )
))
