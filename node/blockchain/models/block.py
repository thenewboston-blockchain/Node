from djongo import models

from node.blockchain.inner_models import Block as PydanticBlock
from node.core.managers import CustomManager


class BlockManager(CustomManager):

    def create(self, *args, **kwargs):
        # This method is blocked intentionally to prohibit adding of invalid blocks
        raise NotImplementedError('One of the `BlockchainFacade.add_block*() methods must be used')

    def get_last_block(self):
        return self.order_by('-_id').first()


class Block(models.Model):
    _id = models.PositiveBigIntegerField('Block number', primary_key=True)
    body = models.BinaryField()

    objects = BlockManager()

    def __str__(self):
        return f'Block number {self._id}'

    def get_block(self) -> PydanticBlock:
        if (block := getattr(self, '_block', None)) is None:
            self._block = block = PydanticBlock.parse_raw(self.body)

        return block

    def save(self, *args, force_insert=True, **kwargs):
        assert force_insert  # must be true for database consistency validation

        # TODO(dmu) LOW: Optimize by querying last block number instead of the entire block
        last_block = Block.objects.get_last_block()
        expected_block_id = 0 if last_block is None else last_block._id + 1
        if expected_block_id != self._id:
            raise ValueError(f'Expected block_id is {expected_block_id}')

        return super().save(*args, force_insert=force_insert, **kwargs)
