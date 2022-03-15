from drf_spectacular.plumbing import get_doc
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.viewsets import ReadOnlyModelViewSet

from node.blockchain.serializers.node import NodeSerializer
from node.core.pagination import CustomLimitOffsetPagination
from node.core.utils.cryptography import get_node_identifier

from ..constants import NODE_DETAILS_EXAMPLE, NODE_LIST_EXAMPLE
from ..tests.examples import load_example

SELF_NODE_ID = 'self'


class NodeViewSet(ReadOnlyModelViewSet):
    serializer_class = NodeSerializer
    queryset = NodeSerializer.Meta.model.objects.order_by('_id')
    pagination_class = CustomLimitOffsetPagination

    @extend_schema(
        summary='Get list of Nodes',
        examples=[OpenApiExample('Get list of nodes', value=load_example(NODE_LIST_EXAMPLE))]
    )
    def list(self, request, *args, **kwargs):  # noqa: A003
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary='Retrieve Node by ID',
        examples=[OpenApiExample('Retrieve Node by ID', value=load_example(NODE_DETAILS_EXAMPLE))],
        description=get_doc(NodeSerializer)
    )
    def retrieve(self, request, *args, **kwargs):
        if self.kwargs.get('pk') == SELF_NODE_ID:
            self.kwargs['pk'] = get_node_identifier()
        return super().retrieve(request, *args, **kwargs)
