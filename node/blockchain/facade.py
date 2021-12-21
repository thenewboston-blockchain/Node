from typing import Type, TypeVar

from node.blockchain.models import AccountState
from node.core.utils.cryptography import get_signing_key
from node.core.utils.misc import set_if_not_none
from node.core.utils.types import AccountLock, BlockIdentifier, SigningKey

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

    def get_block_count(self):
        return get_block_model().objects.count()

    def get_next_block_number(self) -> int:
        # TODO(dmu) HIGH: Implement method via write-through cache
        #                 https://thenewboston.atlassian.net/browse/BC-175
        last_block = get_block_model().objects.get_last_block()
        return last_block._id + 1 if last_block else 0

    def get_next_block_identifier(self) -> BlockIdentifier:
        # TODO(dmu) HIGH: Implement method via write-through cache
        #                 https://thenewboston.atlassian.net/browse/BC-175
        last_block = get_block_model().objects.get_last_block()
        return last_block.make_hash() if last_block else None  # Genesis block has identifier of `null`

    def get_account_lock(self, account_number) -> AccountLock:
        account_state = AccountState.objects.get_or_none(_id=account_number)
        return AccountLock(account_state.account_lock) if account_state else account_number

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

    def update_write_through_cache_schedule(self, schedule):
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

    def update_write_through_cache(self, block_message):
        block_message_update = block_message.update

        accounts = block_message_update.accounts
        if accounts:
            self.update_write_through_cache_accounts(accounts)

        schedule = block_message_update.schedule
        if schedule:
            self.update_write_through_cache_schedule(schedule)
