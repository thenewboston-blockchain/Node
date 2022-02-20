from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from node.blockchain.inner_models.signed_change_request import SignedChangeRequest
from node.blockchain.types import Type
from node.core.fields import PydanticModelBackedJSONField
from node.core.serializers import ValidateUnknownFieldsMixin

API_UNSUPPORTED_TYPES = [
    Type.GENESIS,
    Type.PV_SCHEDULE_UPDATE,
]

API_SUPPORTED_TYPES = {item.value for item in Type if item not in API_UNSUPPORTED_TYPES}


class SignedChangeRequestSerializer(serializers.Serializer, ValidateUnknownFieldsMixin):
    signer = serializers.CharField()
    signature = serializers.CharField()
    message = PydanticModelBackedJSONField()

    def validate(self, attrs):
        message = attrs['message']
        type_ = message.get('type')
        if type_ not in API_SUPPORTED_TYPES:
            raise ValidationError({'message.type': ['Invalid value.']})

        return attrs

    def create(self, validated_data):
        return SignedChangeRequest.parse_obj(validated_data)
