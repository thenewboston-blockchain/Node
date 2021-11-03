from dataclasses import asdict

from django.conf import settings
from pymongo import MongoClient


class Mongo:

    def __init__(self):
        mongo = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
        self.database = mongo[settings.MONGO_DB_NAME]
        self.blocks_collection = self.database['blocks']

    def insert_block(self, *, block):
        self.blocks_collection.insert_one({
            '_id': block.block_number,
            **asdict(block)
        })

    def reset_blockchain(self):
        self.blocks_collection.delete_many({})
