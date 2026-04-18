from django import template

register = template.Library()

@register.filter
def positive(value):
    return abs(value)