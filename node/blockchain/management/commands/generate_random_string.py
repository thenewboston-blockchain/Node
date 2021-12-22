from django.core.management import BaseCommand
from django.utils.crypto import RANDOM_STRING_CHARS, get_random_string

SPECIAL_CHARS = '!@#$%^&*(-_=+)'


class Command(BaseCommand):
    help = 'Generate random string.'  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument('length', type=int, help='Length of random string.')
        parser.add_argument('--special', action='store_true', help='Add special characters to random string.')

    def handle(self, length: int, special: bool, *args, **options):
        characters = RANDOM_STRING_CHARS + SPECIAL_CHARS if special else RANDOM_STRING_CHARS
        random_string = get_random_string(length, characters)
        self.stdout.write(random_string)
