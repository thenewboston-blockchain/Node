from django.core.cache import cache

from v1.blockchain.models.mongo import Mongo


class Blockchain:

    def __init__(self):
        self.mongo = Mongo()

    def add(self, *, block_message: dict):
        self.mongo.insert_block(block_message=block_message)

    def reset(self):
        self.mongo.reset_blockchain()
        cache.clear()
