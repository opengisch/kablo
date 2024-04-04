import uuid

from django.db import models
from django_oapif.decorators import register_oapif_viewset


class AbstractValueList(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_id = models.TextField(null=True)
    code = models.PositiveIntegerField(null=False, blank=False)
    name_fr = models.CharField(max_length=64, blank=True)
    index = models.PositiveIntegerField(null=True)
    is_active = models.BooleanField(default=True, null=False, blank=False)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.original_id}-{self.name_fr}"


@register_oapif_viewset(geom_field=None)
class StatusType(AbstractValueList):
    pass


@register_oapif_viewset(geom_field=None)
class TubeCableProtectionType(AbstractValueList):
    pass


@register_oapif_viewset(geom_field=None)
class CableTensionType(AbstractValueList):
    pass
