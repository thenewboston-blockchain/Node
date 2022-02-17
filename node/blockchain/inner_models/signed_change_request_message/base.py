from node.blockchain.constants import BLOCK_LOCK
from node.blockchain.inner_models.base import BaseModel
from node.blockchain.mixins.crypto import SignableMixin
from node.blockchain.mixins.validatable import ValidatableMixin
from node.blockchain.types import AccountLock, Type
from node.blockchain.utils.lock import lock


class SignedChangeRequestMessage(ValidatableMixin, BaseModel, SignableMixin):
    account_lock: AccountLock
    type: Type  # noqa: A003

    def validate_business_logic(self):
        pass

    @lock(BLOCK_LOCK, expect_locked=True)
    def validate_blockchain_state_dependent(self, blockchain_facade):
        pass
