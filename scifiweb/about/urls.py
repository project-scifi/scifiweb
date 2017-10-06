from itertools import chain

from django.conf.urls import url

import scifiweb.about.views as views
from scifiweb.about.article import Article
from scifiweb.about.article import article_tree
from scifiweb.about.contact import contact


INDEX = Article('', 'About', views.index)

ARTICLES = {
    article.name: article for article in (
        INDEX,
        Article('team', 'Our team', views.team),
        Article('contact', 'Contact us', contact),
    )
}

ARTICLE_TREE = article_tree(ARTICLES.values())


urlpatterns = list(chain(
    (
        url(r'^$', INDEX.render, name='about'),
    ),
    (
        url(r'^{}/$'.format(name), article.render, name=article.url_name)
        for name, article in ARTICLES.items() if name
    )
))
