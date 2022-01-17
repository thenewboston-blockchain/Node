from django import template

from node.core.utils.cryptography import get_node_identifier as get_node_identifier_func

register = template.Library()


@register.simple_tag
def get_node_identifier():
    return get_node_identifier_func()
