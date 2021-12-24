from djongo import models


class Lock(models.Model):
    _id = models.CharField('Lock name', max_length=64, primary_key=True)
