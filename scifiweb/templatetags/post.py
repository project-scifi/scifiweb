import re
import urllib.parse
from collections import namedtuple

from django import template
from django.shortcuts import reverse
from django.utils.safestring import mark_safe

from scifiweb.utils import Link


register = template.Library()


@register.filter
def format_post_date(date):
    return date.strftime('%A, %B %-m, %Y')


@register.filter
def format_post_time(time):
    return time.strftime('%-I:%M %p')


@register.filter
def forward_blog_links(text):
    """A dumb find-and-replace filter which replaces links to the blog
    CMS (WordPress) to the corresponding page on this website.

    This is just a simple safeguard against accidental links to the
    password-protected CMS. All links ought to go to the main website in
    the source post.
    """
    return mark_safe(re.sub(
        r'https?://wp.projectscifi.org',
        reverse('news').rstrip('/'),
        text,
    ))


@register.inclusion_tag('news/partials/tag.html')
def post_tag(tag):
    return {'tag': tag}


@register.inclusion_tag('news/partials/author.html')
def post_author(author):
    return {'author': author}


@register.inclusion_tag('news/partials/category-list.html')
def category_list(categories):
    return {'categories': categories}


PageLink = namedtuple('PageLink', ('link', 'current'))


@register.inclusion_tag('news/partials/page-navigation.html')
def page_navigation(search_params, page_params, total_pages):
    """Insert page navigation links.

    For example, if there are total 20 pages and the current page is 10,
    they look like

        1, ..., 9, 10, 11, ..., 20

    or, on page 3, it looks like

        1, 2, 3, 4, ..., 20

    or, on page 20, it looks like

        1, ..., 19, 20
    """
    def make_link(page):
        params = dict(search_params)
        params.update({
            'page': page,
            'per_page': page_params['per_page'],
        })
        return PageLink(
            link=Link(
                text=str(page),
                url=reverse('news') + '?' + urllib.parse.urlencode(
                    params, doseq=True
                ),
            ),
            current=page == current_page,
        )

    current_page = int(page_params['page'])

    # Start with the first page
    page_links = [make_link(1)]
    radius = 1

    # Add a stretch of pages between the first and last pages
    for p in range(
        max(2, current_page - radius),
        min(current_page + radius + 1, total_pages + 1)
    ):
        page_links.append(make_link(p))

    # And add the last page
    if current_page + radius < total_pages:
        page_links.append(make_link(total_pages))

    # Insert a (literal) ellipsis if there are gaps
    if total_pages > 1:
        if current_page - radius > 2:
            page_links.insert(1, '...')
        if current_page + radius < total_pages - 1:
            page_links.insert(-1, '...')

    # Add previous and next buttons where appropriate
    previous = make_link(current_page - 1) \
        if current_page > 1 else None
    next = make_link(current_page + 1) \
        if current_page < total_pages else None

    return {
        'page_links': page_links,
        'previous': previous,
        'next': next,
    }


@register.inclusion_tag('news/partials/page-info.html')
def page_info(page_params, total_pages, total_posts):
    page = page_params['page']
    per_page = page_params['per_page']
    return {
        'minpost': min((page - 1) * per_page + 1, total_posts),
        'maxpost': min(page * per_page, total_posts),
        'total': total_posts,
    }


@register.simple_tag
def is_selected(params, key, value):
    return 'selected' if params.get(key) == value else ''
