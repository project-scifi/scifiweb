from collections import namedtuple
from functools import partial

from django.shortcuts import render


class Article(namedtuple('Article', ('name', 'title', 'view'))):
    """Metadata about a page for organizing pages into a tree."""
    @property
    def url_name(self):
        """Returns the canonical URL rule name for this article, e.g.
        for `about/contact` it's `info/about/contact`."""
        assert not self.name.startswith('/')
        if self.name:
            return 'info/' + self.name
        else:
            return 'info'

    @property
    def render(self):
        result = partial(self.view, self)
        if hasattr(self.view, '_decorators'):
            for decorator in self.view._decorators:
                result = decorator(result)
        return result


def article_view(template):
    """Returns a partial view function for a generic article."""
    def inner(article, request):
        return render(
            request,
            template,
            {
                'title': article.title,
                'article': article,
            }
        )

    return inner


def article_tree(articles):
    """Nests all articles into a tree based on name."""
    class ArticleNode(dict):
        article = None

        @property
        def children(self):
            return self.values()

        def __format__(self, _):
            return "ArticleNode(article='{}',{})".format(
                self.article.name, super().__format__(_),
            )

    def set_recursive(tree, components, article):
        if not components:
            tree.article = article
        else:
            if components[0] not in tree:
                tree[components[0]] = ArticleNode()
            set_recursive(tree[components[0]], components[1:], article)

    article_tree = ArticleNode()
    for article in articles:
        if article.name == '':
            article_tree.article = article
        else:
            set_recursive(article_tree, article.name.split('/'), article)

    def assert_recursive(tree):
        # Every directory needs a .html file
        assert tree.article, \
            'Missing index article for category. {}'.format(article_tree)
        for child in tree.children:
            assert_recursive(child)

    assert_recursive(article_tree)
    return article_tree
