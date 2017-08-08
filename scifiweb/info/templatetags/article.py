from django import template
from django.core.urlresolvers import reverse

from scifiweb.info.article import get_article_tree
from scifiweb.info.article import get_articles
from scifiweb.utils import Link


register = template.Library()


def _order_tag(ordered):
    return 'ol' if ordered else 'ul'


@register.inclusion_tag('info/partials/link-tree.html')
def article_tree(highlight=None, ordered=False):
    """Renders the article hierarchy as a nested-list tree of links."""
    # Flatten the tree into a list of links and indentation "commands"
    def node_commands(node):
        commands = []
        if node.article.name == highlight:
            # 'a' for 'active'
            commands.append('lia')
        else:
            commands.append('li')
        commands.append(Link(node.article.title, reverse(node.article.url_name)))
        if node.children:
            commands.append('>')
            for child in node.children:
                commands.extend(node_commands(child))
            commands.append('<')
        commands.append('/li')
        return commands

    tree = get_article_tree()
    commands = []
    for node in tree.children:
        commands.extend(node_commands(node))

    return {
        'commands': commands,
        'list_tag': _order_tag(ordered)
    }


@register.inclusion_tag('partials/breadcrumb.html')
def article_breadcrumb(name):
    pieces = name.split('/') if name else []
    names = ['/'.join(pieces[:i]) for i in range(len(pieces) + 1)]
    articles = get_articles()
    articles = [articles[name] for name in names]
    return {
        'components': [Link(article.title, reverse(article.url_name)) for article in articles]
    }
