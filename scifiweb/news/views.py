import datetime
import urllib.parse

import requests
from dateutil.relativedelta import relativedelta
from django.http import Http404
from django.shortcuts import redirect
from django.shortcuts import render
from django.shortcuts import reverse
from django.template.loader import render_to_string

import scifiweb.news.blog as blog
from scifiweb.home import MEMBERS_MAP


EYECATCH_SUBTITLE = 'Making strides in STEM education'


def _post_404(name):
    return Http404("Post '{}' not found.".format(name))


def render_post(request, post):
    member = MEMBERS_MAP.get(post.author.slug)
    if member:
        author_thumbnail = member.thumbnail
    else:
        author_thumbnail = None

    return render(
        request,
        'news/post.html',
        {
            'title': post.title,
            'hero_title': 'Project SCIFI news',
            'subtitle': EYECATCH_SUBTITLE,
            'post': post,
            'other_posts': blog.get_posts(per_page=5),
            'author_thumbnail': author_thumbnail,
        },
    )


def redirect_post_by_id(request, id):
    try:
        id = int(id)
    except ValueError:
        raise _post_404(id)

    post = blog.get_post_by_id(id)

    if post:
        return redirect(post.permalink)
    else:
        raise _post_404(id)


def redirect_post_by_slug(request, slug):
    post = blog.get_post_by_slug(slug)
    if post:
        return redirect(post.permalink)
    else:
        raise _post_404(slug)


def render_post_by_ymds(request, year, month, day, slug):
    post = blog.get_post_by_slug(slug)
    if post:
        date = datetime.date(int(year), int(month), int(day))
        post_date = post.date.date()
        if date == post_date:
            return render_post(request, post)
    raise _post_404(slug)


def redirect_post_by_yms(request, year, month, slug):
    post = blog.get_post_by_slug(slug)
    if post:
        date = datetime.date(int(year), int(month), 1)
        post_date = post.date.date()
        if date == post_date.replace(day=1):
            return redirect(post.permalink)
    raise _post_404(slug)


def redirect_to_daterange(start, end):
    params = urllib.parse.urlencode({
        'after': start.strftime(blog.API_DATETIME_FORMAT),
        'before': end.strftime(blog.API_DATETIME_FORMAT),
    })
    return redirect(reverse('news') + '?' + params)


def redirect_search_by_ymd(request, year, month, day):
    try:
        start = datetime.datetime(int(year), int(month), int(day))
    except ValueError:
        raise Http404
    end = start + datetime.timedelta(days=1, seconds=-1)
    return redirect_to_daterange(start, end)


def redirect_search_by_ym(request, year, month):
    try:
        start = datetime.datetime(int(year), int(month), 1)
    except ValueError:
        raise Http404
    end = start + relativedelta(months=1, seconds=-1)
    return redirect_to_daterange(start, end)


def redirect_search_by_year(request, year):
    try:
        start = datetime.datetime(int(year), 1, 1)
    except ValueError:
        raise Http404
    end = start + relativedelta(years=1, seconds=-1)
    return redirect_to_daterange(start, end)


def validate_search_params(search_params):
    """Checks for invalid search input and removes or replaces bad
    parameters.

    This function operates on the dict in-place, so do `.copy()` or
    `.deepcopy()` on the original to save it.
    """
    if (
        not search_params.get('search')
        and search_params.get('orderby') == 'relevance'
    ):
        # orderby=relevance requires a non-empty search term
        search_params['orderby'] = 'date'


def render_search_titles(search_params, page_params):
    """Returns a triple of `(title, hero_title, subtitle)` appropriate
    for some search parameters and pagination.
    """
    search = search_params.get('search')

    author_names = [
        user.name for user in [
            blog.get_user_by_id(id) for id in search_params.get('author[]', [])
        ] if user
    ]
    tag_names = [
        tag.name for tag in [
            blog.get_tag_by_id(id) for id in search_params.get('tags[]', [])
        ] if tag
    ]
    category_names = [
        category.name for category in [
            blog.get_category_by_id(id)
            for id in search_params.get('categories[]', [])
        ] if category
    ]

    try:
        before_date = datetime.datetime.strptime(
            search_params['before'], blog.API_DATETIME_FORMAT
        ).date()
    except (KeyError, ValueError):
        before_date = None

    try:
        after_date = datetime.datetime.strptime(
            search_params['after'], blog.API_DATETIME_FORMAT
        ).date()
    except (KeyError, ValueError):
        after_date = None

    # Only give a subtitle if a real search was performed
    if any((
        search,
        author_names,
        tag_names,
        category_names,
        before_date,
        after_date
    )):
        did_search = True
        subtitle = render_to_string(
            'news/partials/title.html',
            {
                'search': search,
                'author_names': author_names,
                'tag_names': tag_names,
                'category_names': category_names,
                'before_date': before_date,
                'after_date': after_date,
            }
        )
    else:
        did_search = False
        subtitle = EYECATCH_SUBTITLE

    page = page_params.get('page', 1)
    if page > 1:
        pagenum = 'Page ' + str(page)
    else:
        pagenum = None

    if did_search:
        hero_title = 'News search'
    else:
        hero_title = 'Project SCIFI news'

    components = []
    if did_search:
        components.append(subtitle)
    if pagenum:
        components.append(pagenum)
    components.append(hero_title)
    title = ' – '.join(components)

    return title, hero_title, subtitle


def render_search(request):
    # First, if 'p' is set, redirect to the appropriate post
    post_id = request.GET.get('p')
    if post_id:
        return redirect_post_by_id(request, post_id)

    # Otherwise, do a search

    # Slightly more options are supported than are exposed by the UI; see
    # https://developer.wordpress.org/rest-api/reference/posts/#list-posts
    search_params = {
        # Single-valued params
        param: request.GET[param]
        for param in (
            'after',
            'before',
            'order',
            'orderby',
            'search',
        )
        if param in request.GET
    }
    search_params.update({
        # Multi-valued params
        param: request.GET.getlist(param)
        for param in (
            'author[]',
            'categories[]',
            'tags[]',
        )
        if param in request.GET
    })

    # Pagination parameters are separate so we can generate URLs with
    # the same search params but different page number

    # The min, max and default are set by WordPress, not us
    MIN_PER_PAGE = 10
    MAX_PER_PAGE = 100
    DEFAULT_PER_PAGE = 10
    try:
        page_params = {
            'page': max(1, int(request.GET.get('page', 1))),
            'per_page': max(
                MIN_PER_PAGE,
                min(
                    int(request.GET.get('per_page', DEFAULT_PER_PAGE)),
                    MAX_PER_PAGE
                )
            ),
        }
    except ValueError:
        page_params = {
            'page': 1,
            'per_page': DEFAULT_PER_PAGE,
        }

    # Validation
    validate_search_params(search_params)

    try:
        params = dict(search_params)
        params.update(page_params)
        posts, headers = blog.get_posts(params, headers=True)
    except requests.HTTPError as e:
        # If the request is bad, show zero results (in lieu of validation)
        if e.response.status_code == 400:
            posts, headers = [], {}
        else:
            raise

    # Finally, set up vars for page rendering

    # Fancy templated title
    title, hero_title, subtitle = render_search_titles(
        search_params, page_params
    )

    # Pagination handling
    total_posts = int(headers.get('X-WP-Total', 0))
    total_pages = int(headers.get('X-WP-TotalPages', 1))

    return render(
        request,
        'news/search.html',
        {
            'title': title,
            'hero_title': hero_title,
            'subtitle': subtitle,
            'posts': posts,
            'search_params': search_params,
            'page_params': page_params,
            'total_pages': total_pages,
            'total_posts': total_posts,
        },
    )
