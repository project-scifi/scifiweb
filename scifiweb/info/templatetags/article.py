from collections import namedtuple

from django import template
from django.core.urlresolvers import reverse

from scifiweb.info.urls import ARTICLE_TREE
from scifiweb.info.urls import ARTICLES
from scifiweb.utils import Link


register = template.Library()


@register.inclusion_tag('partials/menu.html')
def article_tree(highlight=None):
    """Renders the article hierarchy as a nested menu with links."""
    LinkNode = namedtuple('Node', ('link', 'children'))

    def to_link_node(node):
        return LinkNode(
            Link(
                node.article.title, reverse(node.article.url_name),
                classes=['is-active'] if node.article.name == highlight else []
            ),
            tuple(to_link_node(child) for child in node.children),
        )

    categories = list(map(to_link_node, ARTICLE_TREE.children))

    for cat in categories:
        cat.link.classes.extend(('is-secondary', 'is-size-6'))

    return {
        'categories': categories,
    }


@register.inclusion_tag('partials/breadcrumb.html')
def article_breadcrumb(name):
    pieces = name.split('/') if name else []
    names = ['/'.join(pieces[:i]) for i in range(len(pieces) + 1)]
    articles = [ARTICLES[name] for name in names]
    return {
        'components': [
            Link(article.title, reverse(article.url_name))
            for article in articles
        ]
    }
