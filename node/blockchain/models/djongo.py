from djongo import models


class ChangeRequest(models.Model):
    signer = models.CharField(max_length=100)
    message = models.CharField(max_length=100)
    signature = models.CharField(max_length=100)

    class Meta:
        abstract = True


class Update(models.Model):
    value = models.IntegerField()

    class Meta:
        abstract = True


class Block(models.Model):
    _id = models.ObjectIdField()
    own_value = models.CharField(max_length=100)
    signed_change_request = models.EmbeddedField(model_container=ChangeRequest)
    updates = models.ArrayField(model_container=Update)

    objects = models.DjongoManager()
