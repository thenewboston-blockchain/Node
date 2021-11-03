from dataclasses import asdict

from django.core.cache import cache

from v1.block_messages.types import BlockMessageTypes
from v1.blockchain.models.mongo import Mongo
from v1.cache.cache_keys import get_account_balance_cache_key, get_account_lock_cache_key


class Blockchain:

    def __init__(self):
        self.mongo = Mongo()

    def add(self, *, block_message: BlockMessageTypes):
        self.update_cache(updates=block_message.updates)
        self.mongo.insert_block(block_message=asdict(block_message))

    def update_cache(self, *, updates):
        self.update_cached_accounts(accounts=updates['accounts'])

    @staticmethod
    def update_cached_accounts(*, accounts):
        for account_number, account_data in accounts.items():
            balance = account_data.get('balance')
            lock = account_data.get('lock')

            if balance:
                account_balance_cache_key = get_account_balance_cache_key(account_number=account_number)
                cache.set(account_balance_cache_key, balance, None)

            if lock:
                account_lock_cache_key = get_account_lock_cache_key(account_number=account_number)
                cache.set(account_lock_cache_key, lock, None)

    def reset(self):
        self.mongo.reset_blockchain()
        cache.clear()
