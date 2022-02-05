from typing import Optional  # noqa: I101

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import Block, BlockMessage, SignedChangeRequest
from node.blockchain.utils.lock import lock
from node.core.database import ensure_in_transaction
from node.core.managers import CustomManager
from node.core.utils.cryptography import derive_public_key, get_signing_key

from ...types import SigningKey

BLOCK_LOCK = 'block'


class BlockManager(CustomManager):

    @ensure_in_transaction
    @lock(BLOCK_LOCK)
    def add_block_from_signed_change_request(
        self,
        signed_change_request: SignedChangeRequest,
        blockchain_facade: BlockchainFacade,
        *,
        signing_key: Optional[SigningKey] = None,
        validate=True
    ) -> Block:
        if validate:
            signed_change_request.validate_business_logic(blockchain_facade)

        block_message = BlockMessage.create_from_signed_change_request(signed_change_request, blockchain_facade)
        # no need to validate the block message since we produced a valid one
        return self.add_block_from_block_message(
            block_message, blockchain_facade, signing_key=signing_key, validate=False, expect_locked=True
        )

    @ensure_in_transaction
    @lock(BLOCK_LOCK)
    def add_block_from_block_message(
        self,
        message: BlockMessage,
        blockchain_facade: BlockchainFacade,
        *,
        signing_key: Optional[SigningKey] = None,
        validate=True
    ) -> Block:
        if validate:
            # TODO(dmu) MEDIUM: Validate block message
            #                   (is it ever used? maybe we just raise NotImplementedError here forever)
            raise NotImplementedError

        signing_key = signing_key or get_signing_key()
        signer = derive_public_key(signing_key)
        signature = message.make_signature(signing_key)

        block = Block(signer=signer, signature=signature, message=message)
        # No need to validate the block since we produced a valid one
        blockchain_facade.add_block(block, validate=False, expect_locked=True)
        return block

    def create(self, *args, **kwargs):
        # This method is blocked intentionally to prohibit adding of invalid blocks
        raise NotImplementedError('One of the `add_block*() methods must be used')

    def get_last_block(self):
        return self.order_by('-_id').first()
