from djongo import models

from node.blockchain.inner_models import BlockMessage
from node.blockchain.validators import HexStringValidator
from node.core.utils.cryptography import derive_public_key
from node.core.utils.types import SigningKey


class BlockManager(models.DjongoManager):

    def create_from_block_message(self, *, message: BlockMessage, signing_key: SigningKey):
        binary_data, signature = message.get_binary_data_and_signature(signing_key)
        return self.create(
            _id=message.number,
            signer=derive_public_key(signing_key),
            signature=signature,
            # TODO(dmu) MEDIUM: We have to decode because of `message = models.TextField()`. Reconsider
            message=binary_data.decode('utf-8'),
        )


class Block(models.Model):
    _id = models.PositiveBigIntegerField('Block number', primary_key=True)
    # TODO(dmu) MEDIUM: Consider using models.BinaryField() for `signer` and `signature` to save storage space
    signer = models.CharField(max_length=64, validators=(HexStringValidator(64),))
    signature = models.CharField(max_length=128, validators=(HexStringValidator(128),))
    # TODO(dmu) MEDIUM: Consider: message = models.BinaryField()
    message = models.TextField()

    objects = BlockManager()

    def __str__(self):
        return f'Block number {self._id}'
