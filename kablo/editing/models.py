import uuid

from django.contrib.gis.db import models
from django.db import transaction

from kablo.network.models import Track


class TrackSplit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    geom = models.LineStringField(srid=2056)
    track = models.ForeignKey(Track, null=False, blank=False, on_delete=models.CASCADE)

    @transaction.atomic
    def save(self, **kwargs):
        if self._state.adding:
            Track.objects.get(id=self.track.id).split(self.geom)
