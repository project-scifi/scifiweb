from django import template
from django.utils.safestring import mark_safe
from PIL import Image


register = template.Library()


def _image_dimensions(path):
    return Image.open('scifiweb/static/' + path).size


@register.filter
def dimensions(value):
    """Reads the dimensions from an image path (relative to
    `STATIC_URL`) and renders `width` and `height` attributes for an
    `<img>` element."""
    width, height = _image_dimensions(value)
    return mark_safe('width="{}" height="{}"'.format(width, height))


@register.filter
def is_portrait(value):
    """Tells whether an image is taller than wide based on its path
    (relative to `STATIC_URL`)."""
    width, height = _image_dimensions(value)
    return height > width
