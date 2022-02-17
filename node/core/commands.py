from django.core.management.base import BaseCommand


class CustomCommand(BaseCommand):

    def write(self, text, ending=None):
        self.stdout.write(text, ending=ending)

    def write_error(self, text):
        self.write(self.style.ERROR(text))

    def write_success(self, text):
        self.write(self.style.SUCCESS(text))

    def write_info(self, text):
        self.write(text)
