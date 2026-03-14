from django import template

register = template.Library()


@register.filter(name="split")
def split(value, arg=","):
    """Split a string by a delimiter. Usage: {{ value|split:',' }}"""
    return [item.strip() for item in value.split(arg) if item.strip()]


@register.filter(name="strip")
def strip_filter(value):
    """Strip whitespace from a string."""
    return value.strip()
