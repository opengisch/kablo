import uuid
from django.db import models
from django.contrib.gis.db.models.aggregates import Union
from django_oapif.decorators import register_oapif_viewset



class AbstractValueList(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_id = models.PositiveIntegerField(null=True)
    original_uuid = models.UUIDField(null=True, editable=True)
    code = models.PositiveIntegerField(null=True)
    name_fr = models.CharField(max_length=64, blank=True)
    index = models.PositiveIntegerField(null=True)
    is_active = models.BooleanField(default=True)

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