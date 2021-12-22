from django.core.management import BaseCommand

from node.core.utils.cryptography import generate_key_pair


class Command(BaseCommand):
    help = 'Generate node signing (private) key'  # noqa: A003

    def handle(self, *args, **options):
        self.stdout.write(generate_key_pair().private)
