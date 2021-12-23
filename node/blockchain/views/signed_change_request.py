from rest_framework import status
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from node.blockchain.facade import BlockchainFacade
from node.blockchain.models import Block
from node.blockchain.serializers.signed_change_request import SignedChangeRequestSerializer
from node.core.exceptions import DRFValidationErrorConverter, ValidationError
from node.core.utils.cryptography import get_signing_key
from node.core.utils.types import NodeRole


class SignedChangeRequestViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = SignedChangeRequestSerializer

    def perform_create(self, serializer):
        signed_change_request = serializer.save()
        blockchain_facade = BlockchainFacade.get_instance()

        if blockchain_facade.get_node_role() == NodeRole.PRIMARY_VALIDATOR:
            try:
                Block.objects.add_block_from_signed_change_request(
                    signed_change_request=signed_change_request,
                    blockchain_facade=blockchain_facade,
                    signing_key=get_signing_key(),
                    validate=True
                )
            except ValidationError as ex:
                raise DRFValidationErrorConverter(ex)
            # TODO(dmu) CRITICAL: Send notifications to CVs about new block
            #                     https://thenewboston.atlassian.net/browse/BC-189
            return

        # TODO CRITICAL: Send signed change request to PV
        #    "NodeClient.get_instance().send_signed_change_request_to_node(primary_validator, signed_change_request)"
        #    https://thenewboston.atlassian.net/browse/BC-190

    # TODO MEDIUM: No need to use "create" method here. serializer.save() should not change serializer.data
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED, headers=headers)
