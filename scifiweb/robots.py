from textwrap import dedent

from django.conf import settings
from django.http import HttpResponse


def robots_dot_txt(request):
    if settings.DEBUG:
        resp = """\
            User-Agent: *
            Disallow: /
        """
    else:
        resp = "User-Agent: *"

    return HttpResponse(
        dedent(resp),
        content_type='text/plain',
    )
