from rest_framework.viewsets import ReadOnlyModelViewSet

from node.blockchain.serializers.node import NodeSerializer
from node.core.pagination import CustomLimitOffsetPagination


class NodeViewSet(ReadOnlyModelViewSet):
    serializer_class = NodeSerializer
    queryset = NodeSerializer.Meta.model.objects.filter(node__isnull=False).order_by('_id')
    pagination_class = CustomLimitOffsetPagination
