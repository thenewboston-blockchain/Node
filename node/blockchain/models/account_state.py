from djongo import models

from node.blockchain.validators import HexStringValidator
from node.core.models import CustomModel


class AccountState(CustomModel):
    identifier = models.CharField(
        'Account number', max_length=64, validators=(HexStringValidator(64),), primary_key=True, db_column='_id'
    )
    balance = models.PositiveBigIntegerField(default=0)
    # TODO(dmu) MEDIUM: Consider using models.BinaryField() for `lock` to save storage space
    account_lock = models.CharField(max_length=64, validators=(HexStringValidator(64),), blank=False)
