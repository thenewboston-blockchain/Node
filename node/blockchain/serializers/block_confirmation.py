from rest_framework import serializers

from node.blockchain.inner_models import BlockConfirmation
from node.core.fields import PydanticModelBackedJSONField
from node.core.serializers import ValidateUnknownFieldsMixin


# TODO(dmu) MEDIUM: Consider implementing BlockConfirmationSerializer as ModelSerializer similar to
#                   node.blockchain.serializers.block.BlockSerializer
class BlockConfirmationSerializer(serializers.Serializer, ValidateUnknownFieldsMixin):
    signer = serializers.CharField()
    signature = serializers.CharField()
    message = PydanticModelBackedJSONField()

    def create(self, validated_data):
        return BlockConfirmation.parse_obj(validated_data)
