from collections import namedtuple


Link = namedtuple('Link', ('text', 'url'))


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
