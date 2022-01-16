from djongo import models

from .manager import BlockManager


class Block(models.Model):
    _id = models.PositiveBigIntegerField('Block number', primary_key=True)
    body = models.BinaryField()

    objects = BlockManager()

    def __str__(self):
        return f'Block number {self._id}'

    def save(self, *args, force_insert=True, **kwargs):
        assert force_insert  # must be true for database consistency validation

        last_block = Block.objects.get_last_block()
        expected_block_id = 0 if last_block is None else last_block._id + 1
        if expected_block_id != self._id:
            raise ValueError(f'Expected block_id is {expected_block_id}')

        return super().save(*args, force_insert=force_insert, **kwargs)
