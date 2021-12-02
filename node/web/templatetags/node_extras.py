from django import template

from node.core.utils.cryptography import get_node_identifier

register = template.Library()


@register.simple_tag
def get_identifier():
    return get_node_identifier()
