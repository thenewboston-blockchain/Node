import logging
from collections import OrderedDict

from rest_framework import serializers

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

    def create(self, validated_data):
        block = PydanticBlock.parse_obj(validated_data)

        block_number = block.get_block_number()
        block_hash = block.make_hash()
        instance, is_created = PendingBlock.objects.get_or_create(
            number=block_number,
            hash=block_hash,
            # TODO(dmu) MEDIUM: It would be more effective to save original request body instead of serializing again
            defaults={'body': block.json()},
        )
        if not is_created:
            logger.warning('Block number %s, hash %s appeared more than once')

        return instance

    class Meta:
        model = ORMBlock
        fields = ('_id', 'signer', 'signature', 'message')  # we are faking list of fields here
        read_only_fields = ('_id',)
