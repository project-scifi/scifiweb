import datetime
from collections import namedtuple

import requests
from cached_property import cached_property
from django.shortcuts import reverse
from django.utils.safestring import mark_safe

from scifiweb.caching import retry
from scifiweb.utils import pathappend


BLOG_API_URL = 'https://wp.projectscifi.org/wp-json/wp/v2/'

API_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'


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
        """Constructs a post from a WordPress API JSON object.

        Note that this expects links to be embedded in the query result,
        i.e. set `_embed=1` when making the API request.
        """
        def get_terms(taxon):
            return [
                Term.from_api_object(term)
                for term_list in obj['_embedded']['wp:term']
                for term in term_list
                if term['taxonomy'] == taxon
            ]

        return Post(
            id=obj['id'],
            slug=obj['slug'],
            date=datetime.datetime.strptime(obj['date'], API_DATETIME_FORMAT),
            modified=datetime.datetime.strptime(
                obj['modified'], API_DATETIME_FORMAT
            ),
            title=obj['title']['rendered'],
            author=User.from_api_object(obj['_embedded']['author'][0]),
            content=mark_safe(obj['content']['rendered']),
            excerpt=mark_safe(obj['excerpt']['rendered']),
            categories=get_terms('category'),
            tags=get_terms('post_tag'),
        )

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
    """Represents the WordPress user, i.e. the author of a post."""
    @staticmethod
    def from_api_object(obj):
        """Constructs a user from a WordPress API JSON object."""
        return User(id=obj['id'], name=obj['name'], slug=obj['slug'])


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
    exactly one category, but may have zero or more tags.
    """
    @staticmethod
    def from_api_object(obj):
        """Constructs a term from a WordPress API JSON object."""
        return Term(
            id=obj['id'],
            name=obj['name'],
            slug=obj['slug'],
            taxonomy=obj['taxonomy'],
        )


@retry(5, requests.ConnectionError)
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

    response = requests.get(
        pathappend(kwargs.get('base_api_url', BLOG_API_URL), endpoint),
        params,
        timeout=1,
    )
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
            **kwargs,
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

    Extra kwargs will be passed to `query_endpoint`. By default, the
    `_embed` parameter is passed and the `Post.from_api_object` function
    is used to construct the list.
    """
    if not params:
        params = {}
    params.setdefault('_embed', True)
    kwargs.setdefault('constructor', Post.from_api_object)
    return query_endpoint('posts', params, **kwargs)


def get_post_by_id(id):
    """Retrieves a post given its unique identifier as an integer.

    Returns None if no such post exists.

    >>> get_post_by_id(1)
    Post(id=1, slug='hello-world', ...)
    """
    return query_keyed_endpoint(
        'posts', int(id),
        params={'_embed': True},
        constructor=Post.from_api_object,
    )


def get_post_by_slug(slug):
    """Retrieves a post given its identifying slug.

    Returns None if no such post exists.

    >>> get_post_by_slug('hello-world')
    Post(id=1, slug='hello-world', ...)
    """
    results = get_posts(params={'slug': slug})
    return results[0] if results else None


def get_users(params=None, **kwargs):
    """Performs a generic query to retrieve a list of users.

    For a list of available arguments, see
    https://developer.wordpress.org/rest-api/reference/users/#list-users
    """
    kwargs.setdefault('constructor', User.from_api_object)
    return query_endpoint('users', params, **kwargs)


def get_user_by_id(id):
    """Retrieves a user given its unique identifier as an integer.

    Returns None if no such user exists.

    >>> get_tag_by_id(1)
    User(id=1, slug='mmcallister', ...)
    """
    id = int(id)
    return query_keyed_endpoint('users', id, constructor=User.from_api_object)


def get_tags(params=None, **kwargs):
    """Performs a generic query to retrieve a list of tags.

    For a list of available arguments, see
    https://developer.wordpress.org/rest-api/reference/tags/#list-tags
    """
    kwargs.setdefault('constructor', Term.from_api_object)
    return query_endpoint('tags', params, **kwargs)


def get_tag_by_id(id):
    """Retrieves a tag given its unique identifier as an integer.

    Returns None if no such tag exists.

    >>> get_tag_by_id(1)
    Term(id=4, slug='test', ...)
    """
    id = int(id)
    return query_keyed_endpoint('tags', id, constructor=Term.from_api_object)


def get_categories(params=None, **kwargs):
    """Performs a generic query to retrieve a list of categories.

    For a list of available arguments, see
    https://developer.wordpress.org/rest-api/reference/categories/#list-categorys
    """
    kwargs.setdefault('constructor', Term.from_api_object)
    return query_endpoint('categories', params, **kwargs)


def get_category_by_id(id):
    """Retrieves a category given its unique identifier as an integer.

    Returns None if no such category exists.

    >>> get_category_by_id(1)
    Term(id=1, slug='uncategorized', ...)
    """
    id = int(id)
    return query_keyed_endpoint(
        'categories', id,
        constructor=Term.from_api_object
    )
