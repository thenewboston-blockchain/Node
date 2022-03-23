import uuid

from djongo import models

from node.blockchain.inner_models import Block as PydanticBlock
from node.core.models import CustomModel


class PendingBlock(CustomModel):

    _id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    number = models.PositiveBigIntegerField()
    hash = models.CharField(max_length=128)  # noqa: A003
    signer = models.CharField(max_length=64)
    body = models.BinaryField()

    def get_block(self) -> PydanticBlock:
        return PydanticBlock.parse_raw(self.body)

    class Meta:
        unique_together = ('number', 'signer')
        ordering = unique_together

    def __str__(self):
        return f'block_number={self.number}, hash={self.hash}'
