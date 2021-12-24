from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from node.blockchain.inner_models.signed_change_request import SignedChangeRequest
from node.core.fields import PydanticModelBackedJSONField
from node.core.serializers import ValidateUnknownFieldsMixin
from node.core.utils.types import Type

API_SUPPORTED_TYPES = {item for item in Type if item != Type.GENESIS}


class SignedChangeRequestSerializer(serializers.Serializer, ValidateUnknownFieldsMixin):
    signer = serializers.CharField()
    signature = serializers.CharField()
    message = PydanticModelBackedJSONField()

    def validate(self, attrs):
        # TODO(dmu) MEDIUM: Test that attrs always have `message` attribute
        message = attrs['message']
        type_ = message.get('type')
        if type_ not in API_SUPPORTED_TYPES:
            raise ValidationError({'message.type': ['Invalid value.']})

        return attrs

    def create(self, validated_data):
        return SignedChangeRequest.parse_obj(validated_data)
