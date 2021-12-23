from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import GenericViewSet

from node.blockchain.facade import BlockchainFacade
from node.blockchain.models import Block
from node.blockchain.serializers.signed_change_request import SignedChangeRequestSerializer
from node.core.utils.cryptography import get_signing_key
from node.core.utils.types import NodeRole


class SignedChangeRequestViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = SignedChangeRequestSerializer

    def perform_create(self, serializer):
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
            return

        # TODO CRITICAL: Send signed change request to PV
        #    "NodeClient.get_instance().send_signed_change_request_to_node(primary_validator, signed_change_request)"
        #    https://thenewboston.atlassian.net/browse/BC-190
        raise NotImplementedError(f'Role {role} is not supported yet')
