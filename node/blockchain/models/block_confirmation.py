import uuid

from djongo import models

from node.core.models import CustomModel


class BlockConfirmation(CustomModel):

    _id = models.UUIDField(primary_key=True, default=uuid.uuid4)  # noqa: A003
    number = models.PositiveBigIntegerField()
    hash = models.CharField(max_length=128)  # noqa: A003
    signer = models.CharField(max_length=64)  # noqa: A003
    body = models.BinaryField()

    class Meta:
        unique_together = ('number', 'hash', 'signer')
        ordering = unique_together

    def __str__(self):
        return f'block_number={self.number}, hash={self.hash}, signer={self.signer}'
