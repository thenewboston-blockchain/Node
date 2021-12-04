from typing import Optional, TypeVar

from django.db import transaction
from djongo import models

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import BlockMessage, SignedChangeRequest
from node.blockchain.mixins.message import MessageMixin
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
        return self.add_block_from_block_message(
            block_message, blockchain_facade, signing_key=signing_key, validate=False
        )

    def add_block_from_block_message(
        self,
        message: BlockMessage,
        blockchain_facade: BlockchainFacade,
        *,
        signing_key: Optional[SigningKey] = None,
        validate=True
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
        with transaction.atomic():
            # TODO(dmu) CRITICAL: Ensure that `with transaction.atomic()` results into transaction or
            #                     save point on MongoDB side
            #                     https://thenewboston.atlassian.net/browse/BC-174
            # We update write through cache here (not in add_block()), because otherwise we would need to
            # deserialize the block (again) to read the message
            blockchain_facade.update_write_through_cache(message)
            return self.add_block(block, validate=False)  # no need to validate the block since we produced a valid one

    def add_block(self, block, *, validate=True) -> B:
        if validate:
            # TODO(dmu) CRITICAL: Validate block
            #                     https://thenewboston.atlassian.net/browse/BC-160
            raise NotImplementedError

        block.save()
        return block

    def create(self, *args, **kwargs):
        # This method is blocked intentionally to prohibit adding of invalid blocks
        raise NotImplementedError('One of the `add_block*() methods must be used')

    def get_last_block(self):
        return self.order_by('-_id').first()


class MessageWrapper(str, MessageMixin):

    def make_binary_message_for_cryptography(self) -> bytes:
        return self.encode('utf-8')  # type: ignore


class Block(models.Model, MessageMixin):
    _id = models.PositiveBigIntegerField('Block number', primary_key=True)
    # TODO(dmu) MEDIUM: Consider using models.BinaryField() for `signer` and `signature` to save storage space
    signer = models.CharField(max_length=64, validators=(HexStringValidator(64),))
    signature = models.CharField(max_length=128, validators=(HexStringValidator(128),))
    # TODO(dmu) MEDIUM: Consider: message = models.BinaryField()
    message = models.TextField()

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

    def get_message(self):
        return MessageWrapper(self.message)
