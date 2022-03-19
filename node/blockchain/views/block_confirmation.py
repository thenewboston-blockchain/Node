from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from node.blockchain.facade import BlockchainFacade
from node.blockchain.models.block_confirmation import BlockConfirmation as ORMBlockConfirmation
from node.blockchain.serializers.block_confirmation import BlockConfirmationSerializer
from node.blockchain.tasks.process_block_confirmations import start_process_block_confirmations_task
from node.core.utils.misc import apply_on_commit


class BlockConfirmationViewSet(GenericViewSet):
    serializer_class = BlockConfirmationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        block_confirmation = serializer.save()

        facade = BlockchainFacade.get_instance()
        next_block_number = facade.get_next_block_number()
        is_next_block_number = block_confirmation.get_number() == next_block_number
        if is_next_block_number:
            block_confirmation.validate_all(facade)
        else:
            block_confirmation.validate_business_logic()

        ORMBlockConfirmation.objects.update_or_create(
            number=block_confirmation.get_number(),
            signer=block_confirmation.signer,
            defaults={
                'hash': block_confirmation.get_hash(),
                'body': block_confirmation.json(),  # TODO(dmu) LOW: Pick request body AS IS instead
            },
        )

        if is_next_block_number and (
            ORMBlockConfirmation.objects.filter(number=next_block_number).count() >= facade.get_minimum_consensus()
        ):
            apply_on_commit(start_process_block_confirmations_task)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
