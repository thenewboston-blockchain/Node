from djongo import models
from djongo.models.fields import DjongoManager

from node.blockchain.validators import HexStringValidator
from node.core.managers import CustomQuerySet
from node.core.models import CustomModel


class ScheduleQuerySet(CustomQuerySet):

    def get_schedule_for_next_block(self):
        from .block import Block
        next_block = Block.objects.get_next_block_number()
        return self.filter(_id__lte=next_block).order_by('-_id').first()


class ScheduleManager(DjongoManager.from_queryset(ScheduleQuerySet)):  # type: ignore
    pass


class Schedule(CustomModel):
    _id = models.PositiveBigIntegerField('Block number', primary_key=True)
    node_identifier = models.CharField(max_length=64, validators=(HexStringValidator(64),), blank=False)

    objects = ScheduleManager()

    def __str__(self):
        return f'{self._id}: {self.node_identifier}'
