from node.blockchain.inner_models.base import BaseModel
from node.blockchain.mixins.crypto import SignableMixin
from node.blockchain.mixins.validatable import ValidatableMixin
from node.blockchain.types import AccountLock, Type


class SignedChangeRequestMessage(ValidatableMixin, BaseModel, SignableMixin):
    account_lock: AccountLock
    type: Type  # noqa: A003

    def validate_business_logic(self):
        pass

    def validate_blockchain_state_dependent(self, blockchain_facade):
        pass
