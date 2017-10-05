from itertools import chain

from django.conf.urls import url

import scifiweb.info.views as views
from scifiweb.info.article import Article
from scifiweb.info.article import article_tree
from scifiweb.info.article import article_view
from scifiweb.info.contact import contact


INDEX = Article('', 'Info', article_view('info/index.html'))

ARTICLES = {
    article.name: article for article in (
        INDEX,
        Article('about', 'About', article_view('info/articles/about.html')),
        Article('about/team', 'Our team', views.team),
        Article('about/contact', 'Contact us', contact),
    )
}

ARTICLE_TREE = article_tree(ARTICLES.values())


urlpatterns = list(chain(
    (
        url(r'^$', INDEX.render, name='info'),
    ),
    (
        url(r'^{}/$'.format(name), article.render, name=article.url_name)
        for name, article in ARTICLES.items() if name
    )
))
