from django import template

register = template.Library()

@register.filter
def sexy_capitals(value):
    str = ''
    for i in range(len(value)):
        if i % 2 == 0:
            str += value[i].upper()
        else:
            str += value[i]
    return str
