import logging

from django.core.cache import cache as django_cache


_logger = logging.getLogger(__name__)


def cache_lookup(key):
    """Look up a key in the cache, raising KeyError if it's a miss."""
    # More good code from ocfweb:
    #
    # The "get" method returns `None` both for cached values of `None`,
    # and keys which aren't in the cache.
    #
    # The recommended workaround is using a sentinel as a default
    # return value for when a key is missing. This allows us to still
    # cache functions which return None.
    cache_miss_sentinel = {}
    retval = django_cache.get(key, cache_miss_sentinel)
    is_hit = retval is not cache_miss_sentinel

    if not is_hit:
        _logger.debug('Cache miss: {}'.format(key))
        raise KeyError('Key "{}" is not in the cache.'.format(key))
    else:
        _logger.debug('Cache hit: {}'.format(key))
        return retval


def cache_lookup_with_fallback(key, fallback, ttl):
    """Returns the value of a key if it is in the cache, or calls a
    fallback function and updates the cache with its result if it is not
    in the cache, returning that instead."""
    try:
        result = cache_lookup(key)
    except KeyError:
        result = fallback()
        django_cache.set(key, result, ttl)
    return result


def cache(ttl=None):
    """Caching function decorator, with an optional ttl.

    The optional ttl (in seconds) specifies how long cache entries
    should live. If not specified, cache entries last until the site
    rolls.
    """
    def outer(fn):
        def inner(*args, **kwargs):
            return cache_lookup_with_fallback(
                _make_function_call_key(fn, args, kwargs),
                lambda: fn(*args, **kwargs),
                ttl=ttl,
            )
        return inner
    return outer


def _make_function_call_key(fn, args, kwargs):
    """Return a key for a cached function call."""
    return (
        '{fn.__module__}#{fn.__name__}'.format(fn=fn),
        tuple(args),
        tuple((k, v) for k, v in sorted(kwargs.items())),
    )
