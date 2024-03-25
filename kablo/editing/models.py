import uuid

from django.contrib.gis.db import models
from django.db import transaction
from django_oapif.decorators import register_oapif_viewset

from kablo.network.models import Track


@register_oapif_viewset(crs=2056)
class TrackSplit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    geom = models.LineStringField(srid=2056)
    force_save = models.BooleanField(default=False)

    @transaction.atomic
    def save(self, **kwargs):
        is_adding = self._state.adding
        super().save(**kwargs)
        # TODO remove when we don't need data anymore
        # if self.force_save:
        if is_adding:
            for track in Track.objects.filter(geom__intersects=self.geom):
                track.split(self.geom)
