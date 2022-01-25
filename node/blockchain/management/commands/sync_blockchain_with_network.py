from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Sync local blockchain with thenewboston blockchain network'  # noqa: A003

    def handle(self, *args, **options):
        # TODO(dmu) CRITICAL: Implement in https://thenewboston.atlassian.net/browse/BC-164
        raise NotImplementedError
