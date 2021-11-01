from django.conf import settings
from django.core.management.base import BaseCommand
from pymongo import MongoClient

"""
python3 manage.py create_from_alpha

Running this script will:
- Create an initial blockchain from alpha
"""


class Command(BaseCommand):
    help = 'Create an initial blockchain from alpha'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        mongo = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
        self.database = mongo[settings.MONGO_DB_NAME]

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Sample message'))
        blocks = self.database['blocks']
        blocks.delete_many({})
