import logging
import random

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
    """Returns the value of a key if it is in the cache, otherwise
    update the cache with a fallback function and return that.
    """
    try:
        result = cache_lookup(key)
    except KeyError:
        result = fallback()
        django_cache.set(key, result, ttl)
        _logger.debug('TTL is: {} {}'.format(ttl, key))
    return result


def cache(ttl=None, key=None, randomize=True):
    """Caching function decorator, with an optional ttl and custom key
    function.

    The ttl (in seconds) specifies how long cache entries should live.
    If not specified, cache entries last until flushed.

    The custom key function should have the call signature of the
    cached function and produce a unique key for the given call.

    By default, TTLs are augmented by a random factor to prevent a cache
    stampede where many keys expire at once. This can be disabled
    per-function.
    """
    if ttl and randomize:
        rand = random.Random()

        # It's dumb, but flake8 doesn't let you assign a lambda
        def make_ttl(): return rand.randint(ttl, int(1.1 * ttl))
    else:
        def make_ttl(): return ttl

    def outer(fn):
        if key:
            make_key = key
        else:
            def make_key(*args, **kwargs):
                return _make_function_call_key(fn, args, kwargs)

        def inner(*args, **kwargs):
            return cache_lookup_with_fallback(
                make_key(*args, **kwargs),
                lambda: fn(*args, **kwargs),
                make_ttl(),
            )
        return inner
    return outer


def _make_function_call_key(fn, args, kwargs):
    """Return a key for a cached function call."""
    return (
        '{fn.__module__}.{fn.__qualname__}'.format(fn=fn),
        tuple(args),
        tuple((k, v) for k, v in sorted(kwargs.items())),
    )


def retry(n, exceptions):
    """A handy decorator which will retry a function call a fixed number
    of times should it fail by raising an exception.

    Only exceptions of the specified type (or types) will trigger a
    retry. If the function raises an exception on the final try, the
    exception is not caught.
    """
    if isinstance(exceptions, (list, set)):
        exceptions = tuple(exceptions)
    elif not isinstance(exceptions, tuple):
        exceptions = (exceptions,)

    def outer(fn):
        def inner(*args, **kwargs):
            for _ in range(n - 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions:
                    continue
            # Don't catch on the last call
            return fn(*args, **kwargs)
        return inner
    return outer


def cache_lookup_only(key):
    """Turns a function into a fallback for a cache lookup.

    Like the `cache` decorator, but never actually writes to the cache.
    This is good for when a function already caches its return value
    somewhere in its body, or for providing a default value for a value
    that is supposed to be cached by a worker process.
    """
    def outer(fn):
        def inner(*args, **kwargs):
            try:
                return cache_lookup(key(*args, **kwargs))
            except KeyError:
                return fn(*args, **kwargs)
        return inner
    return outer
