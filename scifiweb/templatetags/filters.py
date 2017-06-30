from django import template

register = template.Library()

@register.filter
def chunkby(value, n):
    """Splits a list into sublists of length `n`."""
    return [value[i:i + n] for i in range(0, len(value), n)]
