from typing import Type, TypeVar

from node.blockchain.models import AccountState
from node.core.utils.cryptography import get_signing_key
from node.core.utils.misc import set_if_not_none
from node.core.utils.types import AccountLock, BlockIdentifier, SigningKey

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
        # TODO(dmu) HIGH: Implement method via write-through cache
        #                 https://thenewboston.atlassian.net/browse/BC-175
        from node.blockchain.models import Block
        last_block = Block.objects.get_last_block()
        return last_block._id + 1 if last_block else 0

    def get_next_block_identifier(self) -> BlockIdentifier:
        # TODO(dmu) HIGH: Implement method via write-through cache
        #                 https://thenewboston.atlassian.net/browse/BC-175
        from node.blockchain.models import Block
        last_block = Block.objects.get_last_block()
        return last_block.get_message().make_hash() if last_block else None  # Genesis block has identifier of `null`

    def get_account_lock(self, account_number) -> AccountLock:
        account_state = AccountState.objects.get_or_none(_id=account_number)
        return AccountLock(account_state.account_lock) if account_state else account_number

    def update_write_through_cache(self, block_message):
        # TODO(dmu) CRITICAL: Implement updating `schedule`
        #                     https://thenewboston.atlassian.net/browse/BC-176
        for account_number, account_state in block_message.update.accounts.items():
            fields_for_update = {}
            set_if_not_none(fields_for_update, 'account_lock', account_state.account_lock)
            set_if_not_none(fields_for_update, 'balance', account_state.balance)
            node = None if account_state.node is None else account_state.node.dict()
            set_if_not_none(fields_for_update, 'node', node)
            assert fields_for_update

            account_state, is_created = AccountState.objects.get_or_create(
                _id=account_number, defaults=fields_for_update
            )
            if not is_created:
                for field, value in fields_for_update.items():
                    setattr(account_state, field, value)
                account_state.save()
