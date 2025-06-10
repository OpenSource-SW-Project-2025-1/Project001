# accounts/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def split_string(value, arg):
    """
    주어진 문자열(value)을 인자(arg)로 분리하여 리스트로 반환합니다.
    예: "{{ my_string|split_string:',' }}"
    """
    return value.split(arg)

@register.filter
def strip_string(value):
    """
    주어진 문자열(value)의 양 끝 공백을 제거합니다.
    예: "{{ my_string|strip_string }}"
    """
    return value.strip()