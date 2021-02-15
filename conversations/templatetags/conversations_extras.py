from django import template

register = template.Library()


@register.filter(name='startswith')
def startswith(value: str, arg: str):
    """
    Check if a value starts with some string
    """
    return value.startswith(arg)
