import django_filters
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend, RangeFilter
from rest_framework import status
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from node.blockchain.models import Block
from node.blockchain.serializers.block import BlockSerializer
from node.blockchain.tasks.process_pending_blocks import start_process_pending_blocks_task
from node.core.pagination import CustomLimitOffsetNoCountPagination
from node.core.utils.misc import apply_on_commit

from ..constants import LAST_BLOCK_ID


class BlockFilterSet(django_filters.FilterSet):
    block_number = RangeFilter('_id')

    class Meta:
        model = Block
        fields = ('block_number',)


class BlockViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = BlockSerializer
    # TODO(dmu) MEDIUM: We might need to add dynamic ordering later
    queryset = BlockSerializer.Meta.model.objects.order_by('_id')
    pagination_class = CustomLimitOffsetNoCountPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = BlockFilterSet

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        apply_on_commit(start_process_pending_blocks_task)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):  # noqa: A003
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is None:
            serializer = self.get_serializer(queryset, many=True)
        else:
            serializer = self.get_serializer(page, many=True)

        # We use customized response formation to reduce amount of serialization / deserialization
        response_body = '{"results":[' + ','.join(item['body'] for item in serializer.data) + ']}'
        return HttpResponse(content=response_body, content_type='application/json')

    def retrieve(self, request, *args, **kwargs):
        if self.kwargs.get('pk') == LAST_BLOCK_ID:
            instance = Block.objects.order_by('-_id').values('_id').first()
            if instance:
                # We do not use `instance` variable to rely on self.get_object() logic for compatibility purposes
                self.kwargs['pk'] = instance['_id']

        instance = self.get_object()
        return HttpResponse(content=instance.body, content_type='application/json')
