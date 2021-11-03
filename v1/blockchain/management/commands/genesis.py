from datetime import datetime
from hashlib import sha3_256

from django.core.cache import cache
from django.core.management.base import BaseCommand

from v1.blockchain.models.mongo import Mongo
from v1.blocks.models.gensis_block import GenesisBlock
from v1.signed_change_requests.models.signed_change_request import GenesisSignedChangeRequest
from v1.signed_change_requests.models.signed_change_request_message import GenesisSignedChangeRequestMessage
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
        self.mongo = Mongo()

    def handle(self, *args, **options):
        self.wipe_data()

        response = fetch(
            url=(
                f'https://raw.githubusercontent.com/thenewboston-developers/Account-Backups/master/latest_backup/'
                f'latest.json'
            ),
            headers={}
        )

        response_bytes = sort_and_encode(response)
        accounts_hash = sha3_256()
        accounts_hash.update(response_bytes)

        block_identifier = accounts_hash.hexdigest()

        message = GenesisSignedChangeRequestMessage(
            account_lock='',
            accounts=response,
            request_type=''
        )

        signed_change_request = GenesisSignedChangeRequest(
            message=message,
            signature='',
            signer='',
        )

        genesis_block = GenesisBlock(
            block_identifier=block_identifier,
            block_number=0,
            signed_change_request=signed_change_request,
            timestamp=datetime.now(),
            updates={}
        )

        print(genesis_block)

        self.stdout.write(self.style.SUCCESS('Success'))

    def wipe_data(self):
        self.mongo.reset_blockchain()
        cache.clear()
