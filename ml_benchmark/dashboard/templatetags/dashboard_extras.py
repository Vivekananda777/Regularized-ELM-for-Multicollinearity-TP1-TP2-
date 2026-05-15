from django import template

register = template.Library()

@register.filter
def slice_range(value):
    """Return a JSON list like [1,2,3,...,value]"""
    return list(range(1, value + 1))