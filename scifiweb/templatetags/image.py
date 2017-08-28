import os

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from PIL import Image

from scifiweb.caching import cache


register = template.Library()


@cache()
def _image_dimensions(path):
    return Image.open(
        os.path.join(settings.BASE_DIR, 'scifiweb/static/', path)
    ).size


@register.filter
def dimensions(value):
    """Reads the dimensions from a static image path and renders `width`
    and `height` attributes for an `<img>` element."""
    width, height = _image_dimensions(value)
    return mark_safe('width="{}" height="{}"'.format(width, height))


@register.filter
def is_portrait(value):
    """Tells whether an image is taller than wide based on its static
    path."""
    width, height = _image_dimensions(value)
    return height > width


@register.simple_tag(name='svg')
@cache()
def svg(path):
    """Inlines the content of an SVG given its static path."""
    with open(os.path.join(settings.BASE_DIR, 'scifiweb/static/', path)) as f:
        return mark_safe(f.read())
