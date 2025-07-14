from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Allows accessing dictionary items with a variable key in Django templates."""
    return dictionary.get(key)
