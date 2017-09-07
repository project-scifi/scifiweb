import datetime
import logging
from collections import namedtuple

import requests
from cached_property import cached_property
from django.core.cache import cache as django_cache
from django.shortcuts import reverse
from django.utils.safestring import mark_safe

from scifiweb.caching import cache
from scifiweb.caching import retry
from scifiweb.utils import pathappend


_logger = logging.getLogger(__name__)


BLOG_API_URL = 'https://wp.projectscifi.org/wp-json/wp/v2/'

API_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

# Universal among API types
_CACHE_TTL = 600


class Post(namedtuple('Post', (
    'id',
    'slug',
    'date',
    'modified',
    'title',
    'author',
    'content',
    'excerpt',
    'categories',
    'tags',
))):
    """A blog post.

    Blog posts are retrieved from the WordPress API or and cached locally.
    """
    @staticmethod
    def from_api_object(obj):
        """Constructs a post from a WordPress API JSON object."""
        post = Post(
            id=obj['id'],
            slug=obj['slug'],
            date=datetime.datetime.strptime(obj['date'], API_DATETIME_FORMAT),
            modified=datetime.datetime.strptime(obj['modified'], API_DATETIME_FORMAT),
            title=obj['title']['rendered'],
            author=get_user_by_id(int(obj['author'])),
            content=mark_safe(obj['content']['rendered']),
            excerpt=mark_safe(obj['excerpt']['rendered']),
            categories=[get_category_by_id(int(id)) for id in obj['categories']],
            tags=[get_tag_by_id(int(id)) for id in obj['tags']],
        )

        # Update caches
        # XXX: @cached functions update the cache with the same value twice
        django_cache.set(('wp_post_by_id', post.id), post, _CACHE_TTL)
        django_cache.set(('wp_post_id_by_slug', post.slug), post.id, _CACHE_TTL)

        return post

    @cached_property
    def permalink(self):
        """Returns the permalink URL for a post."""
        date = self.date.date()
        return reverse('post', args=(
            '{:04d}'.format(date.year),
            '{:02d}'.format(date.month),
            '{:02d}'.format(date.day),
            self.slug,
        ))


class User(namedtuple('User', (
    'id',
    'slug',
    'name',
))):
    """Represents a WordPress user, i.e. the author of a post."""
    @staticmethod
    def from_api_object(obj):
        """Constructs a user from a WordPress API JSON object."""
        user = User(id=obj['id'], name=obj['name'], slug=obj['slug'])
        django_cache.set(('wp_user_by_id', user.id), user, _CACHE_TTL)
        return user


class Term(namedtuple('Term', (
    'id',
    'slug',
    'name',
    'taxonomy',
))):
    """Represents a term, which is WordPress speak for a label such as a
    tag or category.

    Terms have the usual name, id, and "slug" fields, as well as a
    "taxonomy" field which indicates the type of term. Every post has
    at least one category, but may have zero or more tags.
    """
    @staticmethod
    def from_api_object(obj):
        """Constructs a term from a WordPress API JSON object."""
        term = Term(
            id=obj['id'],
            name=obj['name'],
            slug=obj['slug'],
            taxonomy=obj['taxonomy'],
        )
        django_cache.set(('wp_term_by_id', term.id), term, _CACHE_TTL)
        return term


@retry(5, (requests.ConnectionError, requests.Timeout))
def query_endpoint(endpoint, params=None, **kwargs):
    """Performs a generic query on an API endpoint.

    The `base_api_url` kwarg overrides the API location.

    If the `constructor` kwarg is provided, it will be called on each
    element in the output. Otherwise, the raw dict or list will be
    returned.

    If the `headers` kwarg is `True`, then the output will be a tuple
    `(output, headers)` containing the response headers.
    """
    if not params:
        params = {}

    url = pathappend(kwargs.get('base_api_url', BLOG_API_URL), endpoint)
    _logger.debug('Hit endpoint: {}'.format(url))

    response = requests.get(url, params, timeout=1)
    response.raise_for_status()
    output = response.json()

    constructor = kwargs.get('constructor')
    if constructor:
        if isinstance(output, list):
            result = [constructor(obj) for obj in output]
        else:
            result = constructor(output)
    else:
        result = output

    if kwargs.get('headers'):
        return (result, response.headers)
    else:
        return result


def query_keyed_endpoint(endpoint, key, params=None, **kwargs):
    """Queries an API endpoint that takes a key in the URL, e.g. a
    numeric id.

    If the specified endpoint does not exist (i.e. returns a 404),
    returns None. Keyword arguments are passed to `query_endpoint`.
    """
    try:
        return query_endpoint(
            pathappend(endpoint, str(key)),
            params,
            **kwargs
        )
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            return None
        else:
            raise


def get_posts(params=None, **kwargs):
    """Performs a generic query to retrieve a list of posts.

    For a list of available arguments, see
    https://developer.wordpress.org/rest-api/reference/posts/#list-posts

    Extra kwargs will be passed to `query_endpoint`.
    """
    if not params:
        params = {}
    kwargs.setdefault('constructor', Post.from_api_object)
    return query_endpoint('posts', params, **kwargs)


@cache(ttl=_CACHE_TTL, key=lambda id: ('wp_post_by_id', id))
def get_post_by_id(id):
    """Retrieves a post given its unique identifier as an integer.

    Returns None if no such post exists.

    >>> get_post_by_id(1)
    Post(id=1, slug='hello-world', ...)
    """
    return query_keyed_endpoint(
        'posts', id,
        constructor=Post.from_api_object,
    )


@cache(ttl=_CACHE_TTL, key=lambda slug: ('wp_post_id_by_slug', slug))
def _get_post_id_by_slug(slug):
    """Retrieves the ID of the post with the given slug.

    This exists solely for caching purposes.
    """
    results = get_posts(params={'slug': slug})
    return results[0].id if results else None


def get_post_by_slug(slug):
    """Retrieves a post given its identifying slug.

    Returns None if no such post exists.

    >>> get_post_by_slug('hello-world')
    Post(id=1, slug='hello-world', ...)
    """
    return get_post_by_id(_get_post_id_by_slug(slug))


def get_users(params=None, **kwargs):
    """Performs a generic query to retrieve a list of users.

    For a list of available arguments, see
    https://developer.wordpress.org/rest-api/reference/users/#list-users
    """
    kwargs.setdefault('constructor', User.from_api_object)
    return query_endpoint('users', params, **kwargs)


@cache(ttl=_CACHE_TTL, key=lambda id: ('wp_user_by_id', id))
def get_user_by_id(id):
    """Retrieves a user given its unique identifier as an integer.

    Returns None if no such user exists.

    >>> get_tag_by_id(1)
    User(id=1, slug='mmcallister', ...)
    """
    return query_keyed_endpoint('users', id, constructor=User.from_api_object)


def get_tags(params=None, **kwargs):
    """Performs a generic query to retrieve a list of tags.

    For a list of available arguments, see
    https://developer.wordpress.org/rest-api/reference/tags/#list-tags
    """
    kwargs.setdefault('constructor', Term.from_api_object)
    return query_endpoint('tags', params, **kwargs)


@cache(ttl=_CACHE_TTL, key=lambda id: ('wp_term_by_id', id))
def get_tag_by_id(id):
    """Retrieves a tag given its unique identifier as an integer.

    Returns None if no such tag exists.

    >>> get_tag_by_id(1)
    Term(id=4, slug='test', ...)
    """
    return query_keyed_endpoint('tags', id, constructor=Term.from_api_object)


def get_categories(params=None, **kwargs):
    """Performs a generic query to retrieve a list of categories.

    For a list of available arguments, see
    https://developer.wordpress.org/rest-api/reference/categories/#list-categorys
    """
    kwargs.setdefault('constructor', Term.from_api_object)
    return query_endpoint('categories', params, **kwargs)


@cache(ttl=_CACHE_TTL, key=lambda id: ('wp_term_by_id', id))
def get_category_by_id(id):
    """Retrieves a category given its unique identifier as an integer.

    Returns None if no such category exists.

    >>> get_category_by_id(1)
    Term(id=1, slug='uncategorized', ...)
    """
    return query_keyed_endpoint(
        'categories', id,
        constructor=Term.from_api_object
    )
