import logging
from collections import OrderedDict

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from node.blockchain.facade import BlockchainFacade
from node.blockchain.inner_models import Block as PydanticBlock
from node.blockchain.models import Block as ORMBlock
from node.blockchain.models import PendingBlock

logger = logging.getLogger(__name__)


class BlockSerializer(serializers.ModelSerializer):

    signer = serializers.CharField(min_length=64, max_length=64, write_only=True)
    signature = serializers.CharField(min_length=128, max_length=128, write_only=True)
    message = serializers.JSONField(write_only=True)

    def to_representation(self, instance):
        # This "hack" is needed to reduce deserialization / serialization overhead when reading blocks
        return OrderedDict(body=instance.body)

    def validate_message(self, message):
        is_invalid_number = ((block_number := message.get('number')) is None or
                             block_number < BlockchainFacade.get_instance().get_next_block_number())
        if is_invalid_number:
            raise ValidationError('Invalid number')

        return message

    def create(self, validated_data):
        block = PydanticBlock.parse_obj(validated_data)
        instance, _ = PendingBlock.objects.update_or_create(
            number=block.get_block_number(),
            signer=block.signer,
            # TODO(dmu) MEDIUM: It would be more effective to save original request body instead of serializing again
            defaults={
                'hash': block.make_hash(),
                'body': block.json(),
            },
        )

        return instance

    class Meta:
        model = ORMBlock
        fields = ('_id', 'signer', 'signature', 'message')  # we are faking list of fields here
        read_only_fields = ('_id',)
