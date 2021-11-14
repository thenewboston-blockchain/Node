from djongo import models

from node.blockchain.validators import HexStringValidator


class Account(models.Model):
    _id = models.CharField('Account number', max_length=64, validators=(HexStringValidator(64),), primary_key=True)
    balance = models.IntegerField()
    # TODO(dmu) MEDIUM: Consider using models.BinaryField() for `lock` to save storage space
    lock = models.CharField(max_length=64, validators=(HexStringValidator(64),))

    objects = models.DjongoManager()
