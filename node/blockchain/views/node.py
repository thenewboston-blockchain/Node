from django_filters import BaseInFilter, FilterSet, NumberFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ReadOnlyModelViewSet

from node.blockchain.models import Node
from node.blockchain.serializers.node import NodeSerializer
from node.core.pagination import CustomLimitOffsetPagination
from node.core.utils.cryptography import get_node_identifier

SELF_NODE_ID = 'self'


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class NodeFilterSet(FilterSet):
    roles = NumberInFilter(field_name='_id', method='filter_by_role_types')

    def filter_by_role_types(self, queryset, _, value):
        # if identifiers := get_identifiers_by_roles(value):
        #     queryset = queryset.filter(_id__in=identifiers)
        return queryset

    class Meta:
        model = Node
        fields = ['roles']


class NodeViewSet(ReadOnlyModelViewSet):
    serializer_class = NodeSerializer
    queryset = NodeSerializer.Meta.model.objects.order_by('identifier')
    pagination_class = CustomLimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = NodeFilterSet

    def retrieve(self, request, *args, **kwargs):
        if self.kwargs.get('pk') == SELF_NODE_ID:
            self.kwargs['pk'] = get_node_identifier()
        return super().retrieve(request, *args, **kwargs)
