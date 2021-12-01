from typing import Type as TypingType
from typing import TypeVar, cast

from pydantic import root_validator

from node.core.utils.cryptography import derive_public_key, is_signature_valid
from node.core.utils.types import AccountNumber, Signature, SigningKey

from .base import BaseModel
from .signed_change_request_message.base import SignedChangeRequestMessage
from .signed_change_request_message.genesis import GenesisSignedChangeRequestMessage
from .signed_change_request_message.node_declaration import NodeDeclarationSignedChangeRequestMessage

T = TypeVar('T', bound='SignedChangeRequest')


class SignedChangeRequest(BaseModel):
    signer: AccountNumber
    signature: Signature
    message: SignedChangeRequestMessage

    @classmethod
    def create_from_signed_change_request_message(
        cls: TypingType[T], *, message: SignedChangeRequestMessage, signing_key: SigningKey
    ) -> T:
        from node.blockchain.inner_models.type_map import get_signed_change_request_subclass
        class_ = get_signed_change_request_subclass(message.type)
        assert class_  # because message.type should be validated by now
        class_ = cast(TypingType[T], class_)

        return class_(
            signer=derive_public_key(signing_key),
            signature=message.make_signature(signing_key),
            message=message,
        )

    @classmethod
    def parse_obj(cls, *args, **kwargs):
        obj = super().parse_obj(*args, **kwargs)
        type_ = obj.message.type
        from node.blockchain.inner_models.type_map import get_signed_change_request_subclass
        class_ = get_signed_change_request_subclass(type_)
        assert class_  # because message.type should be validated by now

        if cls == class_:  # avoid recursion
            return obj

        return class_.parse_obj(*args, **kwargs)

    @root_validator
    def validate_signature(cls, values):
        if cls == SignedChangeRequest:
            # This workaround is fine because we never validate signature for `SignedChangeRequest` instances.
            # Signature validation makes sense for child classes only since they define the actual structure being
            # signed
            return values

        signer = values.get('signer')
        message = values.get('message')
        signature = values.get('signature')
        if (
            # TODO(dmu) MEDIUM: How is it possible that signer, signature, message can be empty?
            not all((signer, signature, message)) or
            not is_signature_valid(signer, message.make_binary_data_for_cryptography(), signature)
        ):
            raise ValueError('invalid signature')

        return values

    def get_type(self):
        return self.message.type


class GenesisSignedChangeRequest(SignedChangeRequest):
    message: GenesisSignedChangeRequestMessage


class NodeDeclarationSignedChangeRequest(SignedChangeRequest):
    message: NodeDeclarationSignedChangeRequestMessage
