from djongo import models

from node.blockchain.validators import HexStringValidator
from node.core.models import CustomModel


class Schedule(CustomModel):
    _id = models.PositiveBigIntegerField('Block number', primary_key=True)
    node_identifier = models.CharField(max_length=64, validators=(HexStringValidator(64),), blank=False)
