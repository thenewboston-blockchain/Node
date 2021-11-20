from typing import Type as TypingType
from typing import TypeVar

from node.core.utils.cryptography import derive_public_key
from node.core.utils.types import AccountNumber, Signature, SigningKey, Type

from .base import BaseModel
from .signed_change_request_message.base import SignedChangeRequestMessage
from .signed_change_request_message.genesis import GenesisSignedChangeRequestMessage

T = TypeVar('T', bound='SignedChangeRequest')


class SignedChangeRequest(BaseModel):
    signer: AccountNumber
    signature: Signature
    message: SignedChangeRequestMessage

    @classmethod
    def create_from_signed_change_request_message(
        cls: TypingType[T], *, message: SignedChangeRequestMessage, signing_key: SigningKey
    ) -> T:
        return cls(
            signer=derive_public_key(signing_key),
            signature=message.get_signature(signing_key),
            message=message,
        )

    @classmethod
    def parse_obj(cls, *args, **kwargs):
        obj = super().parse_obj(*args, **kwargs)
        type_ = obj.message.type
        class_ = TYPE_MAP.get(type_)
        if not class_:
            # TODO(dmu) MEDIUM: Raise validation error instead
            raise Exception(f'Unknown type: {type_}')

        if cls == class_:  # avoid recursion
            return obj

        return class_.parse_obj(*args, **kwargs)


class GenesisSignedChangeRequest(SignedChangeRequest):
    message: GenesisSignedChangeRequestMessage


TYPE_MAP = {Type.GENESIS: GenesisSignedChangeRequest}
