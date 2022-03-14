from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from node.blockchain.facade import BlockchainFacade
from node.blockchain.models.block_confirmation import BlockConfirmation as ORMBlockConfirmation
from node.blockchain.serializers.block_confirmation import BlockConfirmationSerializer


class BlockConfirmationViewSet(GenericViewSet):
    serializer_class = BlockConfirmationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        block_confirmation = serializer.save()

        facade = BlockchainFacade.get_instance()
        if facade.get_next_block_number() == block_confirmation.get_number():
            block_confirmation.validate_all(facade)

        ORMBlockConfirmation.objects.update_or_create(
            number=block_confirmation.get_number(),
            hash=block_confirmation.get_hash(),
            signer=block_confirmation.signer,
            body=block_confirmation.json(),  # TODO(dmu) LOW: Pick request body as is instead
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)
