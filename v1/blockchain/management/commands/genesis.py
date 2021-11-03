from dataclasses import asdict
from datetime import datetime
from hashlib import sha3_256

from django.core.cache import cache
from django.core.management.base import BaseCommand

from v1.block_messages.gensis import GenesisBlockMessage
from v1.blockchain.models.blockchain import Blockchain
from v1.blockchain.models.mongo import Mongo
from v1.constants.block_types import GENESIS
from v1.signed_change_request_messages.genesis import GenesisSignedChangeRequestMessage
from v1.signed_change_requests.genesis import GenesisSignedChangeRequest
from v1.utils.network import fetch
from v1.utils.signing import encode_key, generate_signature, get_public_key
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
        self.blockchain = Blockchain()
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
        public_key = encode_key(key=get_public_key())

        signed_change_request_message = GenesisSignedChangeRequestMessage(
            accounts=response,
            lock=public_key,
            request_type=GENESIS
        )
        signed_change_request = GenesisSignedChangeRequest(
            message=signed_change_request_message,
            signature=generate_signature(message=asdict(signed_change_request_message)),
            signer=public_key,
        )

        genesis_block_message = GenesisBlockMessage(
            block_identifier=accounts_hash.hexdigest(),
            block_number=0,
            block_type=signed_change_request_message.request_type,
            signed_change_request=signed_change_request,
            timestamp=str(datetime.now()),
            updates={}
        )

        self.blockchain.add(block_message=asdict(genesis_block_message))
        self.stdout.write(self.style.SUCCESS('Success'))

    def wipe_data(self):
        self.mongo.reset_blockchain()
        cache.clear()
