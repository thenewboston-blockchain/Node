from rest_framework.viewsets import ReadOnlyModelViewSet

from node.blockchain.serializers.node import NodeSerializer
from node.core.pagination import CustomLimitOffsetPagination
from node.core.utils.cryptography import get_node_identifier

SELF_NODE_ID = 'self'


class NodeViewSet(ReadOnlyModelViewSet):
    serializer_class = NodeSerializer
    queryset = NodeSerializer.Meta.model.objects.order_by('_id')
    pagination_class = CustomLimitOffsetPagination

    def retrieve(self, request, *args, **kwargs):
        if self.kwargs.get('pk') == SELF_NODE_ID:
            self.kwargs['pk'] = get_node_identifier()
        return super().retrieve(request, *args, **kwargs)
