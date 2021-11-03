from django.conf import settings
from pymongo import MongoClient

from v1.utils.signing import encode_key, generate_signature, get_public_key


class Mongo:

    def __init__(self):
        mongo = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
        self.database = mongo[settings.MONGO_DB_NAME]
        self.blocks_collection = self.database['blocks']

    def insert_block(self, *, block_message: dict):
        self.blocks_collection.insert_one({
            '_id': block_message['block_number'],
            'message': block_message,
            'signature': generate_signature(message=block_message),
            'signer': encode_key(key=get_public_key()),
        })

    def reset_blockchain(self):
        self.blocks_collection.delete_many({})
