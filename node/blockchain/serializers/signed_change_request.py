from pydantic.error_wrappers import ValidationError as PydanticValidationError
from rest_framework import serializers

from node.blockchain.inner_models.signed_change_request import SignedChangeRequest
from node.core.exceptions import DRFValidationErrorConverter
from node.core.serializers import ValidateUnknownFieldsMixin


class SignedChangeRequestSerializer(serializers.Serializer, ValidateUnknownFieldsMixin):
    signer = serializers.CharField()
    signature = serializers.CharField()
    message = serializers.JSONField()

    def create(self, validated_data):
        try:
            return SignedChangeRequest.parse_obj(validated_data)
        except PydanticValidationError as ex:
            raise DRFValidationErrorConverter(ex)
