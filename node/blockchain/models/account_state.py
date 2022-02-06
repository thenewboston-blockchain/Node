from djongo import models

from node.blockchain.validators import HexStringValidator
from node.core.fields import NullableJSONField
from node.core.models import CustomModel


class AccountState(CustomModel):
    _id = models.CharField('Account number', max_length=64, validators=(HexStringValidator(64),), primary_key=True)
    balance = models.PositiveBigIntegerField(default=0)
    # TODO(dmu) MEDIUM: Consider using models.BinaryField() for `lock` to save storage space
    account_lock = models.CharField(max_length=64, validators=(HexStringValidator(64),), blank=False)

    # TODO(dmu) MEDIUM: Should we have node as models.TextField() instead and deserialize it with Pydantic model
    node = NullableJSONField(blank=True, null=True)
