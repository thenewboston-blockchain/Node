from typing import Type, TypeVar

from node.blockchain.inner_models import Node
from node.blockchain.mixins.crypto import HashableStringWrapper
from node.blockchain.models import AccountState
from node.blockchain.types import AccountLock, AccountNumber, BlockIdentifier, NodeRole, SigningKey
from node.core.utils.cryptography import get_signing_key
from node.core.utils.misc import set_if_not_none

T = TypeVar('T', bound='BlockchainFacade')


def get_block_model():
    # We need it to resolve circular imports
    from node.blockchain.models import Block
    return Block


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

    @staticmethod
    def get_block_count():
        return get_block_model().objects.count()

    @staticmethod
    def get_next_block_number() -> int:
        # TODO(dmu) HIGH: Implement method via write-through cache
        #                 https://thenewboston.atlassian.net/browse/BC-175
        last_block = get_block_model().objects.get_last_block()
        return last_block._id + 1 if last_block else 0

    @staticmethod
    def get_next_block_identifier() -> BlockIdentifier:
        # TODO(dmu) HIGH: Implement method via write-through cache
        #                 https://thenewboston.atlassian.net/browse/BC-175
        last_block = get_block_model().objects.get_last_block()
        assert last_block  # this method should never be used for creating genesis block

        return HashableStringWrapper(last_block.body).make_hash()

    @staticmethod
    def get_account_lock(account_number) -> AccountLock:
        account_state = AccountState.objects.get_or_none(_id=account_number)
        return AccountLock(account_state.account_lock) if account_state else account_number

    @staticmethod
    def get_account_balance(account_number: AccountNumber) -> int:
        account_state = AccountState.objects.get_or_none(_id=account_number)
        return account_state.balance if account_state else 0

    @staticmethod
    def update_write_through_cache_accounts(accounts):
        for account_number, account_state in accounts.items():
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

    @staticmethod
    def update_write_through_cache_schedule(schedule):
        # TODO(dmu) HIGH: Add more unittests once PV schedule block is implemented
        #                 - Add PV
        #                 - Remove PV
        #                 - Replace PV
        #                 https://thenewboston.atlassian.net/browse/BC-193
        from node.blockchain.models import Schedule

        # TODO(dmu) LOW: More optimal algorithm would not delete all schedule record, but only what should be deleted
        Schedule.objects.all().delete()
        for block_number, node_identifier in schedule.items():
            Schedule.objects.create(_id=block_number, node_identifier=node_identifier)

    @staticmethod
    def clear():
        get_block_model().objects.all().delete()

        AccountState.objects.all().delete()
        from node.blockchain.models import Schedule
        Schedule.objects.all().delete()

    def update_write_through_cache(self, block):
        block_message_update = block.message.update

        accounts = block_message_update.accounts
        if accounts:
            self.update_write_through_cache_accounts(accounts)

        schedule = block_message_update.schedule
        if schedule:
            self.update_write_through_cache_schedule(schedule)

    def get_node_role(self):
        # TODO CRITICAL: Implement method to determine which role has Node.
        #                https://thenewboston.atlassian.net/browse/BC-191
        return NodeRole.PRIMARY_VALIDATOR

    def get_primary_validator(self) -> Node:
        # TODO(dmu) CRITICAL: Implement this method
        #                     https://thenewboston.atlassian.net/browse/BC-212
        raise NotImplementedError
