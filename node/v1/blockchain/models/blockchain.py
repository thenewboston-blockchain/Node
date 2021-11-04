from dataclasses import asdict

from v1.block_messages.types import BlockMessageTypes
from v1.blockchain.models.mongo import Mongo


class Blockchain:

    def __init__(self):
        self.mongo = Mongo()

    def add(self, *, block_message: BlockMessageTypes):
        self.mongo.insert_block(block_message=asdict(block_message))

    def reset(self):
        self.mongo.reset_blockchain()
