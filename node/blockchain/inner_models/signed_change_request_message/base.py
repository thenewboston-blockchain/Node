from node.blockchain.inner_models.base import BaseModel
from node.blockchain.mixins.crypto import SignableMixin
from node.core.utils.types import AccountLock, Type


class SignedChangeRequestMessage(BaseModel, SignableMixin):
    account_lock: AccountLock
    # TODO(dmu) MEDIUM: Maybe `type` type should be defined as `int` instead of `IntEnum` for simpler serialization
    #                   (let's see how it works with Django REST Framework)
    type: Type  # noqa: A003
