from django.conf import settings
from pymongo import MongoClient

from v1.utils.signing import encode_key, generate_signature, get_public_key


class Mongo:

    def __init__(self):
        mongo = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
        self.database = mongo[settings.MONGO_DB_NAME]
        self.accounts_collection = self.database['accounts']
        self.blocks_collection = self.database['blocks']
        self.config_collection = self.database['config']
        self.nodes_collection = self.database['nodes']
        self.schedule_collection = self.database['schedule']

    def _update_accounts(self, accounts):
        for account_number, account_data in accounts.items():
            self.accounts_collection.update_one(
                {'_id': account_number},
                {'$set': account_data},
                upsert=True
            )

    def _update_config_from_block_data(self, *, block_identifier, block_number):
        config = {
            'last_block_hash': block_identifier,
            'last_block_number': block_number
        }

        if block_number == 0:
            config |= {
                'last_snapshot_block_hash': None,
                'last_snapshot_block_number': None,
                'last_snapshot_file_url': None
            }

        self.update_config(config=config)

    def _update_nodes(self, nodes):
        for account_number, node_data in nodes.items():
            self.nodes_collection.update_one(
                {'_id': account_number},
                {'$set': node_data},
                upsert=True
            )

    def _update_schedule(self, validators):
        for position, validator in validators.items():
            self.schedule_collection.update_one(
                {'_id': position},
                {'$set': validator},
                upsert=True
            )

    def insert_block(self, *, block_message: dict):
        block_identifier = block_message['block_identifier']
        block_number = block_message['block_number']
        updates = block_message['updates']

        self.blocks_collection.insert_one({
            '_id': str(block_number),
            'message': block_message,
            'signature': generate_signature(message=block_message),
            'signer': encode_key(key=get_public_key()),
        })

        self._update_config_from_block_data(
            block_identifier=block_identifier,
            block_number=block_number
        )

        self._update_accounts(accounts=updates['accounts'])
        self._update_nodes(nodes=updates['nodes'])
        self._update_schedule(validators=updates['validators'])

    def reset_blockchain(self):
        self.accounts_collection.delete_many({})
        self.blocks_collection.delete_many({})
        self.config_collection.delete_many({})
        self.nodes_collection.delete_many({})
        self.schedule_collection.delete_many({})

    def update_config(self, *, config: dict):
        self.config_collection.update_one(
            {'_id': '0'},
            {'$set': config},
            upsert=True
        )
