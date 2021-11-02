from dataclasses import asdict
from hashlib import sha3_256

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand
from pymongo import MongoClient

from v1.blockchain.models.account import Account
from v1.blockchain.models.mongo import Mongo
from v1.blockchain.models.snapshot import Snapshot
from v1.utils.network import fetch
from v1.utils.tools import sort_and_encode

"""
python3 manage.py genesis

Running this script will:
- Download the latest alpha backup file
- Create the genesis block
"""


class Command(BaseCommand):
    help = 'Download the latest alpha backup file and create the genesis block'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        mongo = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
        self.database = mongo[settings.MONGO_DB_NAME]
        self.blocks_collection = self.database['blocks']

    def handle(self, *args, **options):
        self.wipe_data()

        response = fetch(
            url=(
                f'https://raw.githubusercontent.com/thenewboston-developers/Account-Backups/master/latest_backup/'
                f'latest.json'
            ),
            headers={}
        )

        snapshot = self.snapshot_from_alpha_backup(alpha_backup=response)
        snapshot = asdict(snapshot)
        snapshot_bytes = sort_and_encode(snapshot)

        snapshot_hash = sha3_256()
        snapshot_hash.update(snapshot_bytes)
        block_identifier = snapshot_hash.hexdigest()

        Mongo().insert_block(
            block_identifier=block_identifier,
            block_number=0,
            message=snapshot
        )

        self.stdout.write(self.style.SUCCESS('Success'))

    @staticmethod
    def snapshot_from_alpha_backup(*, alpha_backup):
        accounts = {}

        for account_number, account_data in alpha_backup.items():
            accounts[account_number] = Account(
                balance=account_data['balance'],
                balance_lock=account_data['balance_lock']
            )

        return Snapshot(accounts=accounts, nodes={})

    def wipe_data(self):
        self.blocks_collection.delete_many({})
        cache.clear()
