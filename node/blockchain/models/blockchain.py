from dataclasses import asdict

from .mongo import Mongo
from .types import BlockMessageTypes


class Blockchain:

    def __init__(self):
        self.mongo = Mongo()

    def add(self, *, block_message: BlockMessageTypes):
        self.mongo.insert_block(block_message=asdict(block_message))

    def reset(self):
        self.mongo.reset_blockchain()
