from djongo import models

from node.blockchain.validators import HexStringValidator


class Node(models.Model):
    _id = models.CharField('Identifier', max_length=64, validators=(HexStringValidator(64),), primary_key=True)
    fee = models.IntegerField()
    # TODO(dmu) MEDIUM: Is there a better type to represent a list of strings for `network_addresses`?
    network_addresses = models.JSONField()

    objects = models.DjongoManager()
