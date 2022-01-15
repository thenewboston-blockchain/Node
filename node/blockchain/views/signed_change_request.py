from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from node.blockchain.facade import BlockchainFacade
from node.blockchain.models import Block
from node.blockchain.serializers.signed_change_request import SignedChangeRequestSerializer
from node.blockchain.types import NodeRole
from node.core.clients.node import NodeClient
from node.core.utils.cryptography import get_signing_key


class SignedChangeRequestViewSet(GenericViewSet):
    serializer_class = SignedChangeRequestSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        signed_change_request = serializer.save()

        blockchain_facade = BlockchainFacade.get_instance()
        role = blockchain_facade.get_node_role()
        if role == NodeRole.PRIMARY_VALIDATOR:
            Block.objects.add_block_from_signed_change_request(
                signed_change_request=signed_change_request,
                blockchain_facade=blockchain_facade,
                signing_key=get_signing_key(),
                validate=True
            )
            # TODO(dmu) CRITICAL: Send notifications to CVs about new block
            #                     https://thenewboston.atlassian.net/browse/BC-189
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        pv_node = blockchain_facade.get_primary_validator()
        response = NodeClient.get_instance().send_scr_to_node(pv_node, signed_change_request)
        return HttpResponse(
            response.content, status=response.status_code, content_type=response.headers.get('content-type')
        )
