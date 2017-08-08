import os
from collections import namedtuple

from django.shortcuts import render
from django.template import Context
from django.template.loader import get_template
from django.template.loader_tags import BlockNode
from django.template.loader_tags import ExtendsNode

from scifiweb.caching import cache
from scifiweb.settings import BASE_DIR


ARTICLES_ROOT = os.path.join(
    BASE_DIR, 'scifiweb/info/templates/info/articles/'
)


class Article(namedtuple('Article', ('name', 'title', 'template', 'url_name'))):
    @staticmethod
    def from_template(template_path):
        """Loads an article from the path to its template.

        The given template path is relative to `info/articles/`, i.e.
        `about/contact.html` creates the page `/info/about/contact/`
        under using the template `info/articles/about/contact.html`.
        """
        name = os.path.splitext(template_path)[0]
        template = 'info/articles/' + template_path
        title = _render_block(template, 'title')
        url_name = 'info/' + name
        return Article(name, title, template, url_name)

    @property
    def renderer(self):
        """Returns a view function for the article."""
        return lambda request: render(
            request,
            self.template,
            {
                'title': self.title,
                'article': self,
            }
        )


def _render_block(template_name, block_name):
    """This code snippet renders the contents of the named block from a
    template, which may extend other templates."""
    def inner_render(template):
        for node in template.nodelist:
            if isinstance(node, BlockNode) and node.name == block_name:
                return node.render(Context())
            elif isinstance(node, ExtendsNode):
                return inner_render(node)
        raise Exception(
            "Node '{}' could not be found in template '{}'."
            .format(block_name, template_name)
        )

    return inner_render(get_template(template_name).template)


Node = namedtuple('Node', ('article', 'children'))


def get_articles():
    """Returns all articles in a list"""
    return _articles_and_tree()[0]


def get_article_tree():
    """Returns a tree structure containing the hierarchy of articles."""
    return _articles_and_tree()[1]


@cache()
def _articles_and_tree():
    articles = {'': INDEX}
    article_tree = Node(INDEX, [])

    def find_nodes(path):
        nodes = {}

        # Handle files first...
        for f in os.listdir(os.path.join(ARTICLES_ROOT, path)):
            relpath = os.path.join(path, f)
            fullpath = os.path.join(ARTICLES_ROOT, relpath)

            if os.path.isfile(fullpath):
                article = Article.from_template(relpath)
                articles[article.name] = article
                nodes[article.name] = Node(article, [])

        # ... then directories
        for f in os.listdir(os.path.join(ARTICLES_ROOT, path)):
            relpath = os.path.join(path, f)
            fullpath = os.path.join(ARTICLES_ROOT, relpath)

            if os.path.isdir(fullpath):
                nodes[relpath].children.extend(find_nodes(relpath))

        return nodes.values()

    article_tree.children.extend(find_nodes(''))
    return articles, article_tree


INDEX = Article(
    name='',
    title=_render_block('info/index.html', 'title'),
    template='info/index.html',
    url_name='info',
)
