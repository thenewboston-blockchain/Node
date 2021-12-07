from django.db import models
from djongo.models.fields import DjongoManager


class CustomQuerySet(models.QuerySet):

    def get_or_none(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except self.model.DoesNotExist:
            pass


class CustomManager(DjongoManager.from_queryset(CustomQuerySet)):  # type: ignore
    pass
