from djongo import models
from djongo.models import ObjectIdField


class Lock(models.Model):
    _id = ObjectIdField()
    name = models.CharField(max_length=64, unique=True)
