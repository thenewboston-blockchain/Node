import uuid

from djongo import models

from node.blockchain.inner_models import BlockConfirmation as PydanticBlockConfirmation
from node.core.managers import CustomManager
from node.core.models import CustomModel


class BlockConfirmationManager(CustomManager):

    def create_from_block_confirmation(self, block_confirmation: PydanticBlockConfirmation):
        return self.create(
            number=block_confirmation.get_number(),
            signer=block_confirmation.signer,
            hash=block_confirmation.get_hash(),
            body=block_confirmation.json(),
        )

    def update_or_create_from_block_confirmation(self, block_confirmation: PydanticBlockConfirmation):
        return self.update_or_create(
            number=block_confirmation.get_number(),
            signer=block_confirmation.signer,
            defaults={
                'hash': block_confirmation.get_hash(),
                'body': block_confirmation.json(),
            },
        )


class BlockConfirmation(CustomModel):

    _id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    number = models.PositiveBigIntegerField()
    hash = models.CharField(max_length=128)  # noqa: A003
    signer = models.CharField(max_length=64)
    body = models.BinaryField()

    objects = BlockConfirmationManager()

    class Meta:
        unique_together = ('number', 'signer')
        ordering = unique_together

    def get_block_confirmation(self) -> PydanticBlockConfirmation:
        return PydanticBlockConfirmation.parse_raw(self.body)

    def __str__(self):
        return f'block_number={self.number}, signer={self.signer}, hash={self.hash}'
