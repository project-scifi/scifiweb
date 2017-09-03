import os
from collections import namedtuple
from functools import partial

from django.conf import settings
from django.shortcuts import render

from scifiweb.utils import render_block


ARTICLES_ROOT = os.path.join(
    settings.BASE_DIR, 'scifiweb/info/templates/info/articles/'
)


class Article(namedtuple('Article', ('name', 'title', 'view'))):
    @staticmethod
    def from_template(template_path):
        """Constructs an article from the path to its template.

        The given template path is relative to `info/articles/`, e.g.
        `about/contact.html` creates the page `/info/about/contact/`
        using the template `info/articles/about/contact.html`.

        The view function must take an `article` object and a `request`.
        """
        assert not template_path.startswith('/')
        name = os.path.splitext(template_path)[0]
        template = os.path.join('info/articles/', template_path)
        title = render_block(template, 'title')
        return Article(name, title, article_view(template))

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
        return partial(self.view, self)


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


def get_normal_articles():
    """Walks the filesystem to find generic articles that don't require
    their own view function."""
    articles = []
    for dirpath, _, filenames in os.walk(ARTICLES_ROOT):
        for f in filenames:
            fullpath = os.path.join(dirpath, f)
            if os.path.isfile(fullpath):
                relpath = os.path.relpath(fullpath, ARTICLES_ROOT)
                articles.append(Article.from_template(relpath))

    return articles


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
