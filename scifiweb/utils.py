from collections import namedtuple

from django.template import Context
from django.template.loader import get_template
from django.template.loader_tags import BlockNode
from django.template.loader_tags import ExtendsNode


class Link(namedtuple('Link', ('text', 'url', 'classes'))):
    """A configurable class for inserting links into templates."""
    __slots__ = ()

    def __new__(cls, text, url, classes=()):
        return super().__new__(cls, text, url, classes)


def pathappend(base, suffix, sep='/'):
    """Appends a path component to a base file path or URL.

    Like os.path.join, but always treats the suffix as a relative path.
    The separator can be any single character, by default `/`.

    >>> pathappend('http://example.com/api', 'test/')
    'http://example.com/api/test/'
    >>> pathappend('/etc', '/test')
    '/etc/test'
    >>> pathappend('12:34:56:', ':78:90', sep=':')
    '12:34:56:78:90'
    """
    return base.rstrip(sep) + sep + suffix.lstrip(sep)


def render_block(template_name, block_name, context=Context()):
    """This code snippet renders the contents of the named block from a
    template, which may extend other templates.

    Optionally takes a context as a `dict` or a Django `Context` object.
    """
    def inner_render(template):
        for node in template.nodelist:
            if isinstance(node, BlockNode) and node.name == block_name:
                return node.render(context)
            elif isinstance(node, ExtendsNode):
                return inner_render(node)
        raise ValueError(
            "Node '{}' could not be found in template '{}'."
            .format(block_name, template_name)
        )

    return inner_render(get_template(template_name).template)
