from django.db import models
from django.utils import timezone


class CommonInfoAbstractModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    last_modified_at = models.DateTimeField(auto_now=True)
    soft_delete = models.BooleanField(default=False)

    class Meta:
        abstract = True
