from collections import namedtuple


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


def store_decorators(decorators):
    """Sets a list of decorators as the attribute `_decorators` on a
    function.

    This is for the purpose of applying decorators to a higher-level
    wrapping function.
    """
    def outer(fn):
        fn._decorators = decorators
        return fn
    return outer
