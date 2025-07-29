from django import template

register = template.Library()

@register.filter
def split(value, delimiter):
    """Split a string by delimiter and return a list"""
    return value.split(delimiter)