import uuid

from django.contrib.gis.db import models
from django.db import transaction
from django_oapif.decorators import register_oapif_viewset

from kablo.network.models import Track


@register_oapif_viewset(crs=2056)
class TrackSplit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    geom = models.LineStringField(srid=2056)
    track = models.ForeignKey(Track, null=False, blank=False, on_delete=models.CASCADE)

    @transaction.atomic
    def save(self, **kwargs):
        if self._state.adding:
            Track.objects.get(id=self.track.id).split(self.geom)
