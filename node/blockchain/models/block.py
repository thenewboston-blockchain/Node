from typing import Optional, TypeVar

from djongo import models

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import BlockMessage, SignedChangeRequest
from node.blockchain.validators import HexStringValidator
from node.core.utils.cryptography import derive_public_key, get_signing_key
from node.core.utils.types import SigningKey

B = TypeVar('B', bound='Block')


class BlockManager(models.DjongoManager):
    # TODO(dmu) CRITICAL: Lock blockchain for the period of validation and adding blocks
    #                     https://thenewboston.atlassian.net/browse/BC-158
    def add_block_from_signed_change_request(
        self,
        signed_change_request: SignedChangeRequest,
        blockchain_facade: BlockchainFacade,
        *,
        signing_key: Optional[SigningKey] = None,
        validate=True
    ) -> B:
        if validate:
            # TODO(dmu) CRITICAL: Validate signed change request
            #                     https://thenewboston.atlassian.net/browse/BC-159
            pass

        block_message = BlockMessage.create_from_signed_change_request(signed_change_request, blockchain_facade)
        # no need to validate the block message since we produced a valid one
        return self.add_block_from_block_message(block_message, signing_key=signing_key, validate=False)

    def add_block_from_block_message(
        self, message: BlockMessage, *, signing_key: Optional[SigningKey] = None, validate=True
    ) -> B:
        if validate:
            # TODO(dmu) MEDIUM: Validate block message
            #                   (is it ever used? maybe we just raise NotImplementedError here forever)
            raise NotImplementedError

        signing_key = signing_key or get_signing_key()
        binary_data, signature = message.make_binary_data_and_signature(signing_key)
        block = Block(
            _id=message.number,
            signer=derive_public_key(signing_key),
            signature=signature,
            # TODO(dmu) MEDIUM: We have to decode because of `message = models.TextField()`. Reconsider
            message=binary_data.decode('utf-8'),
        )
        return self.add_block(block, validate=False)  # no need to validate the block since we produced a valid one

    def add_block(self, block, *, validate=True) -> B:
        if validate:
            # TODO(dmu) CRITICAL: Validate block
            #                     https://thenewboston.atlassian.net/browse/BC-160
            raise NotImplementedError

        # TODO(dmu) CRITICAL: Make sure that the database is properly locked on low level so we do not overwrite
        #                     existing block (force INSERT for MongoDB :) ) - something similar to select_for_update()
        block.save(force_insert=True)
        return block

    def create(self, *args, **kwargs):
        # This method is blocked intentionally to prohibit adding of invalid blocks
        raise NotImplementedError('One of the `add_block*() methods must be used')


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
