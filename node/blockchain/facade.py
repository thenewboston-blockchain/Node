from typing import Type, TypeVar

from node.core.utils.cryptography import get_signing_key
from node.core.utils.types import BlockIdentifier, SigningKey

T = TypeVar('T', bound='BlockchainFacade')


class BlockchainFacade:

    _instance = None

    def __init__(self, signing_key: SigningKey):
        self.signing_key = signing_key

    @classmethod
    def get_instance(cls: Type[T]) -> T:
        instance = cls._instance
        if not instance:
            instance = cls(signing_key=get_signing_key())
            cls.set_instance_cache(instance)

        return instance

    @classmethod
    def set_instance_cache(cls: Type[T], instance: T):
        cls._instance = instance

    @classmethod
    def clear_instance_cache(cls):
        cls._instance = None

    def get_next_block_number(self) -> int:
        raise NotImplementedError

    def get_next_block_identifier(self) -> BlockIdentifier:
        raise NotImplementedError
