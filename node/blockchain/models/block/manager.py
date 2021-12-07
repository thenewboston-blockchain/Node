from typing import TYPE_CHECKING, Optional  # noqa: I101

from django.db import transaction
from djongo import models

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import BlockMessage, SignedChangeRequest
from node.core.utils.cryptography import derive_public_key, get_signing_key
from node.core.utils.types import SigningKey

if TYPE_CHECKING:
    from .model import Block


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
    ) -> 'Block':
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
    ) -> 'Block':
        if validate:
            # TODO(dmu) MEDIUM: Validate block message
            #                   (is it ever used? maybe we just raise NotImplementedError here forever)
            raise NotImplementedError

        signing_key = signing_key or get_signing_key()
        binary_data, signature = message.make_binary_data_and_signature(signing_key)

        from .model import Block
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

    def add_block(self, block, *, validate=True) -> 'Block':
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
