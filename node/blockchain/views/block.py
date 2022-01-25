from django.http import HttpResponse
from rest_framework.viewsets import ReadOnlyModelViewSet

from node.blockchain.models import Block
from node.blockchain.serializers.block import BlockSerializer
from node.core.pagination import CustomLimitOffsetNoCountPagination

LAST_BLOCK_ID = 'last'


class BlockViewSet(ReadOnlyModelViewSet):
    serializer_class = BlockSerializer
    # TODO(dmu) MEDIUM: We might need to add dynamic filtering and ordering later
    queryset = BlockSerializer.Meta.model.objects.order_by('_id')
    pagination_class = CustomLimitOffsetNoCountPagination

    def list(self, request, *args, **kwargs):  # noqa: A003
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is None:
            serializer = self.get_serializer(queryset, many=True)
        else:
            serializer = self.get_serializer(page, many=True)

        # We use customized response formation to reduce amount of serialization / deserialization
        response_body = '[' + ','.join(serializer.data) + ']'
        return HttpResponse(content=response_body, content_type='application/json')

    def retrieve(self, request, *args, **kwargs):
        if self.kwargs.get('pk') == LAST_BLOCK_ID:
            instance = Block.objects.order_by('-_id').values('_id').first()
            if instance:
                # We do not use instance to rely on self.get_object() logic for compatibility purposes
                self.kwargs['pk'] = instance['_id']

        instance = self.get_object()
        return HttpResponse(content=instance.body, content_type='application/json')
