from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from node.blockchain.facade import BlockchainFacade
from node.blockchain.serializers.signed_change_request import SignedChangeRequestSerializer
from node.blockchain.tasks.send_new_block import start_send_new_block_task
from node.blockchain.types import NodeRole
from node.core.clients.node import NodeClient
from node.core.utils.cryptography import get_signing_key
from node.core.utils.misc import apply_on_commit


class SignedChangeRequestViewSet(GenericViewSet):
    serializer_class = SignedChangeRequestSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        signed_change_request = serializer.save()

        blockchain_facade = BlockchainFacade.get_instance()
        role = blockchain_facade.get_node_role()
        if role == NodeRole.PRIMARY_VALIDATOR:
            block = blockchain_facade.add_block_from_signed_change_request(
                signed_change_request=signed_change_request, signing_key=get_signing_key(), validate=True
            )
            # TODO(dmu) HIGH: When a PV Schedule update block is added notifications will be sent the new list
            #                 of validators instead of the list existed before the block (fix it)
            #                 https://thenewboston.atlassian.net/browse/BC-268
            block_number = block.get_block_number()  # it is important to put block number to a variable first
            apply_on_commit(lambda: start_send_new_block_task(block_number))
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        pv_node = blockchain_facade.get_primary_validator()
        signed_change_request.validate_business_logic()
        response = NodeClient.get_instance().send_signed_change_request(pv_node, signed_change_request)
        return HttpResponse(
            response.content, status=response.status_code, content_type=response.headers.get('content-type')
        )
