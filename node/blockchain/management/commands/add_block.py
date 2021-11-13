from django.core.management.base import BaseCommand
from node.blockchain.models.djongo import Block


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('block_number', type=int)

    def handle(self, *args, **options):
        block = Block(
            _id=options['block_number'],
            own_value='Hey',
            signed_change_request={'signer': 'signer1', 'signature': 'signature1', 'message': 'message1'},
            updates=[{'value': 10}],
        )
        block.save()

        # Block.objects.create(
        #     _id=options['block_number'],
        #     own_value='Hey',
        #     signed_change_request={'signer': 'signer1', 'signature': 'signature1', 'message': 'message1'},
        #     updates=[{'value': 10}],
        # )
