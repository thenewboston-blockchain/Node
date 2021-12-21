import json

from djongo import models

from node.blockchain.constants import JSON_CRYPTO_KWARGS
from node.blockchain.mixins.crypto import HashableMixin
from node.blockchain.validators import HexStringValidator

from .manager import BlockManager


class Block(models.Model, HashableMixin):
    _id = models.PositiveBigIntegerField('Block number', primary_key=True)
    # TODO(dmu) MEDIUM: Consider using models.BinaryField() for `signer` and `signature` to save storage space
    signer = models.CharField(max_length=64, validators=(HexStringValidator(64),))
    signature = models.CharField(max_length=128, validators=(HexStringValidator(128),))
    # TODO(dmu) MEDIUM: Consider: message = models.BinaryField()
    message = models.TextField()

    objects = BlockManager()

    def __str__(self):
        return f'Block number {self._id}'

    def make_binary_message_for_cryptography(self) -> bytes:
        dict_ = {'signer': self.signer, 'signature': self.signature, 'message': self.message}
        return json.dumps(dict_, **JSON_CRYPTO_KWARGS).encode('utf-8')  # type: ignore

    def save(self, *args, force_insert=True, **kwargs):
        assert force_insert  # must be true for database consistency validation

        last_block = Block.objects.get_last_block()
        expected_block_id = 0 if last_block is None else last_block._id + 1
        if expected_block_id != self._id:
            raise ValueError(f'Expected block_id is {expected_block_id}')

        return super().save(*args, force_insert=force_insert, **kwargs)
