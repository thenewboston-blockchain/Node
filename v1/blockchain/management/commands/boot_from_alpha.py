from django.conf import settings
from django.core.management.base import BaseCommand
from pymongo import MongoClient

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

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Sample message'))
        blocks = self.database['blocks']
        blocks.delete_many({})

        response = fetch(
            url=(
                f'https://raw.githubusercontent.com/thenewboston-developers/Account-Backups/master/latest_backup/'
                f'latest.json'
            ),
            headers={}
        )

        block = generate_block(
            message=response,
            signing_key=get_signing_key()
        )

        blocks.insert_one(block)
