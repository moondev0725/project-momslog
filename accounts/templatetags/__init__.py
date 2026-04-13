from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """딕셔너리에서 key로 value를 가져옵니다."""
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''
