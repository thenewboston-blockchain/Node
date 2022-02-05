from typing import Optional  # noqa: I101

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import Block, BlockMessage, SignedChangeRequest
from node.blockchain.utils.lock import lock
from node.core.database import ensure_in_transaction
from node.core.managers import CustomManager

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
        return blockchain_facade.add_block_from_block_message(
            block_message, signing_key=signing_key, validate=False, expect_locked=True
        )

    def create(self, *args, **kwargs):
        # This method is blocked intentionally to prohibit adding of invalid blocks
        raise NotImplementedError('One of the `add_block*() methods must be used')

    def get_last_block(self):
        return self.order_by('-_id').first()
