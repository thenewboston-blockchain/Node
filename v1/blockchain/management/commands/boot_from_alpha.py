from dataclasses import asdict

from django.conf import settings
from django.core.management.base import BaseCommand
from pymongo import MongoClient

from v1.blockchain.models.account_state import AccountState
from v1.blockchain.models.blockchain_state import BlockchainState
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

    @staticmethod
    def blockchain_state_from_alpha_backup(*, alpha_backup):
        account_states = {}

        for account_number, account_data in alpha_backup.items():
            account_states[account_number] = AccountState(
                balance=account_data['balance'],
                balance_lock=account_data['balance_lock']
            )

        return BlockchainState(account_states=account_states)

    def handle(self, *args, **options):
        blocks = self.database['blocks']
        blocks.delete_many({})

        response = fetch(
            url=(
                f'https://raw.githubusercontent.com/thenewboston-developers/Account-Backups/master/latest_backup/'
                f'latest.json'
            ),
            headers={}
        )

        blockchain_state = self.blockchain_state_from_alpha_backup(alpha_backup=response)
        blockchain_state = asdict(blockchain_state)

        block = generate_block(
            message=blockchain_state,
            signing_key=get_signing_key()
        )
        blocks.insert_one({
            '_id': 0,
            **block
        })

        self.stdout.write(self.style.SUCCESS('Success'))
