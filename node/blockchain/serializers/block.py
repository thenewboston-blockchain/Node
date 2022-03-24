import logging
from collections import OrderedDict

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import Block as PydanticBlock
from node.blockchain.models import Block as ORMBlock
from node.blockchain.models import PendingBlock
from node.blockchain.tasks.process_pending_blocks import start_process_pending_blocks_task
from node.core.utils.misc import apply_on_commit

logger = logging.getLogger(__name__)


class BlockSerializer(serializers.ModelSerializer):

    signer = serializers.CharField(min_length=64, max_length=64, write_only=True)
    signature = serializers.CharField(min_length=128, max_length=128, write_only=True)
    message = serializers.JSONField(write_only=True)

    def to_representation(self, instance):
        # This "hack" is needed to reduce deserialization / serialization overhead when reading blocks
        return OrderedDict(body=instance.body)

    def create(self, validated_data):
        block = PydanticBlock.parse_obj(validated_data)

        facade = BlockchainFacade.get_instance()
        block_number = block.get_block_number()
        next_block_number = facade.get_next_block_number()
        if block_number < next_block_number:
            raise ValidationError('Invalid block number')

        if block_number == next_block_number:
            # Preliminary validation (we will revalidate it later) therefore providing `bypass_lock_validation=True`
            block.validate_all(facade, bypass_lock_validation=True)
        else:
            block.validate_business_logic()

        instance, _ = PendingBlock.objects.update_or_create(
            number=block.get_block_number(),
            signer=block.signer,
            # TODO(dmu) MEDIUM: It would be more effective to save original request body instead of serializing again
            defaults={
                'hash': block.make_hash(),
                'body': block.json(),
            },
        )

        if block_number == next_block_number:
            apply_on_commit(start_process_pending_blocks_task)

        return instance

    class Meta:
        model = ORMBlock
        fields = ('_id', 'signer', 'signature', 'message')  # we are faking list of fields here
        read_only_fields = ('_id',)
