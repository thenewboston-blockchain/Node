from django.core.management.base import BaseCommand

"""
python3 manage.py sync

Running this script will:
- attempt to sync blockchains with the target node
"""


class Command(BaseCommand):
    help = 'Sync blockchains with the target node'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Yo'))
