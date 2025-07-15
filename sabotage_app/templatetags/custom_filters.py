from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """辞書のキーでルックアップを行うフィルター"""
    if dictionary is None:
        return None
    return dictionary.get(key)
