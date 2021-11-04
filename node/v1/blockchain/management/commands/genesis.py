from dataclasses import asdict
from datetime import datetime

from django.core.management.base import BaseCommand

from v1.accounts.models.alpha_account import AlphaAccount
from v1.block_messages.models.gensis import GenesisBlockMessage
from v1.blockchain.models.blockchain import Blockchain
from v1.blockchain.models.mongo import Mongo
from v1.constants.block_types import GENESIS
from v1.signed_change_request_messages.models.genesis import GenesisSignedChangeRequestMessage
from v1.signed_change_requests.models.genesis import GenesisSignedChangeRequest
from v1.utils.network import fetch
from v1.utils.signing import encode_key, generate_signature, get_public_key

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
        self.blockchain = Blockchain()
        self.mongo = Mongo()

    @staticmethod
    def get_updated_accounts(accounts) -> dict[str, dict]:
        results = {}

        for account_number, account_data in accounts.items():
            results[account_number] = {
                'balance': account_data['balance'],
                'lock': account_data['balance_lock']
            }

        return results

    @staticmethod
    def get_updated_nodes() -> dict[str, dict]:
        public_key = encode_key(key=get_public_key())

        return {
            public_key: {
                'fee_amount': 1,
                'network_addresses': ['http://78.107.238.40:8555/']
            }
        }

    def handle(self, *args, **options):
        self.blockchain.reset()

        accounts: dict[str, AlphaAccount] = fetch(
            url=(
                f'https://raw.githubusercontent.com/thenewboston-developers/Account-Backups/master/latest_backup/'
                f'latest.json'
            ),
            headers={}
        )

        public_key = encode_key(key=get_public_key())

        signed_change_request_message = GenesisSignedChangeRequestMessage(
            accounts=accounts,
            lock=public_key,
            request_type=GENESIS
        )
        signed_change_request = GenesisSignedChangeRequest(
            message=signed_change_request_message,
            signature=generate_signature(message=asdict(signed_change_request_message)),
            signer=public_key,
        )
        genesis_block_message = GenesisBlockMessage(
            block_identifier=None,
            block_number=0,
            block_type=signed_change_request_message.request_type,
            signed_change_request=signed_change_request,
            timestamp=str(datetime.now()),
            updates={
                'accounts': self.get_updated_accounts(accounts),
                'nodes': self.get_updated_nodes(),
                'validators': {
                    '0': {
                        'first_block': 0,
                        'last_block': 99,
                        'node': public_key
                    }
                }
            }
        )

        self.blockchain.add(block_message=genesis_block_message)
        self.stdout.write(self.style.SUCCESS('Success'))
