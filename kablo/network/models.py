import uuid

from django.contrib.gis.db import models
from django.contrib.gis.db.models.aggregates import Union
from django.contrib.gis.geos import LineString
from django.db import transaction

from kablo.core.geometry import Intersects, SplitLine


class NetworkNode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    geom = models.PointField(srid=2056)


class Track(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    identifier = models.TextField(null=True, blank=True)
    geom = models.MultiLineStringField(srid=2056)

    @transaction.atomic
    def save(self, **kwargs):
        # calling the super method causes the state flags to change, so save the original value in advance
        is_adding = self._state.adding
        super().save(**kwargs)
        if is_adding:
            order_index = 0
            sections = []

            for part_geom in self.geom:
                section = Section(
                    geom=part_geom,
                    track=self,
                    order_index=order_index,
                )
                order_index += 1
                sections.append(section)

            Section.objects.bulk_create(sections)

    @transaction.atomic
    def split(self, split_line: LineString):
        has_split = False
        order_index = 0
        sections_qs = (
            Section.objects.filter(track=self)
            .annotate(
                splitted_geom=models.Case(
                    models.When(
                        models.Q(Intersects("geom", split_line)),
                        then=SplitLine("geom", split_line),
                    ),
                    output_field=models.GeometryCollectionField(),
                ),
            )
            .order_by("order_index")
        )

        for section in sections_qs:

            if section.splitted_geom:
                has_split = True
                for split_part_idx, split_part in enumerate(section.splitted_geom):
                    if split_part_idx == 0:
                        section.geom = split_part
                    else:
                        order_index += 1
                        section = section.clone()

                    section.order_index = order_index
                    section.save()
            elif has_split:
                # update the ordering indexes on following sections
                section.order_index = order_index
                section.save()
            else:
                # no need to update index if no intersection occurred
                pass

            order_index += 1

        if has_split:
            self.geom = Section.objects.filter(track=self).aggregate(
                union=Union("geom")
            )["union"]
            self.save()


class Section(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    geom = models.LineStringField(srid=2056)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    order_index = models.IntegerField(default=0, null=False, blank=False)

    network_node_start = models.ForeignKey(
        NetworkNode,
        null=True,
        blank=True,
        related_name="network_node_start",
        on_delete=models.SET_NULL,
    )
    network_node_end = models.ForeignKey(
        NetworkNode,
        null=True,
        blank=True,
        related_name="network_node_end",
        on_delete=models.SET_NULL,
    )

    class Meta:
        unique_together = ("track", "order_index")

    def clone(self):
        new_kwargs = dict(
            [
                (fld.name, getattr(self, fld.name))
                for fld in self._meta.fields
                if fld.name != "id"
            ]
        )
        return Section(**new_kwargs)


class Tube(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sections = models.ManyToManyField(Section)


class TubeSection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tube = models.ForeignKey(Tube, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    order_index = models.IntegerField(default=1)


class Station(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    geom = models.PointField(srid=2056)


class Node(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class Reach(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    node_1 = models.ForeignKey(
        Node, related_name="node_1", blank=True, null=True, on_delete=models.SET_NULL
    )
    node_2 = models.ForeignKey(
        Node, related_name="node_2", blank=True, null=True, on_delete=models.SET_NULL
    )


class Cable(Reach):
    tubes = models.ManyToManyField(Tube)


class VirtualNode(Node):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)


class Switch(Reach):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)


class Terminal(Node):
    pass
