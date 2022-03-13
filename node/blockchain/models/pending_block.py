import uuid

from djongo import models

from node.core.models import CustomModel


class PendingBlock(CustomModel):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)  # noqa: A003
    number = models.PositiveBigIntegerField()
    hash = models.CharField(max_length=128)  # noqa: A003
    body = models.BinaryField()

    class Meta:
        unique_together = ('number', 'hash')
        ordering = unique_together

    def __str__(self):
        return f'block_number={self.number}, hash={self.hash}'
