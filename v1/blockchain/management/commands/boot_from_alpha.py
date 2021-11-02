from dataclasses import asdict

from django.conf import settings
from django.core.management.base import BaseCommand
from pymongo import MongoClient

from v1.blockchain.models.account import Account
from v1.blockchain.models.snapshot import Snapshot
from v1.utils.blocks import generate_block
from v1.utils.network import fetch
from v1.utils.signing import get_signing_key

"""
python3 manage.py boot_from_alpha

Running this script will:
- Download the latest alpha backup file
- Create the initial blockchain
"""


class Command(BaseCommand):
    help = 'Boot from the latest alpha backup file'

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

        # TODO: Write a helper function for all of this
        block = generate_block(
            message=snapshot,
            signing_key=get_signing_key()
        )
        self.blocks_collection.insert_one({
            '_id': 0,
            'block_identifier': 1,  # TODO: Hash the block
            **block
        })

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
