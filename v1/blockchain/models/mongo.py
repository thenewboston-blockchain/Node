from django.conf import settings
from pymongo import MongoClient

from v1.blocks.utils import generate_block
from v1.utils.signing import get_signing_key


class Mongo:

    def __init__(self):
        mongo = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
        self.database = mongo[settings.MONGO_DB_NAME]
        self.blocks_collection = self.database['blocks']

    def insert_block(self, *, block_identifier, block_number, message):
        block = generate_block(
            message=message,
            signing_key=get_signing_key()
        )
        self.blocks_collection.insert_one({
            '_id': block_number,
            'block_identifier': block_identifier,
            **block
        })

    def reset_blockchain(self):
        self.blocks_collection.delete_many({})
