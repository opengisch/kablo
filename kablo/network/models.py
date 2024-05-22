import uuid

from django.contrib.gis.db import models
from django.contrib.gis.db.models.aggregates import MakeLine as MakeLineAgg
from django.contrib.gis.db.models.aggregates import Union
from django.contrib.gis.geos import LineString
from django.db import transaction
from django.db.models import ExpressionWrapper, F, Max, Value
from django.db.models.functions import Cast, Least
from django_oapif.decorators import register_oapif_viewset

from kablo.core.functions import (
    EndPoint,
    Force3D,
    Intersects,
    Length2d,
    LineMerge,
    LineSubstring,
    MakeLine,
    OffsetCurve,
    ProjectZOnLine,
    SplitLine,
    StartPoint,
)
from kablo.valuelist.models import CableTensionType, StatusType, TubeCableProtectionType


class NetworkNode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    geom = models.PointField(srid=2056, dim=3)


@register_oapif_viewset(crs=2056)
class Track(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    original_id = models.TextField(null=True, editable=True)
    geom = models.MultiLineStringField(srid=2056, dim=3)

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
                        section.geom = split_part

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


@register_oapif_viewset(crs=2056)
class Section(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    geom = models.LineStringField(srid=2056, dim=3)
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
        ordering = ["track_id", "order_index"]

    def clone(self):
        new_kwargs = dict()
        for field in self._meta.fields:
            if field.name != "id":
                new_kwargs[field.name] = getattr(self, field.name)
        return Section(**new_kwargs)


@register_oapif_viewset(crs=2056)
class Cable(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fake_id = models.UUIDField(default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    identifier = models.TextField(null=True, blank=True)
    original_id = models.TextField(null=True, editable=True)
    tension = models.ForeignKey(
        CableTensionType,
        null=True,
        on_delete=models.SET_NULL,
    )
    status = models.ForeignKey(
        StatusType,
        null=True,
        on_delete=models.SET_NULL,
    )
    geom = models.LineStringField(srid=2056, dim=3, null=True)

    def compute_geom(self):
        # TODO: check geometry exists + is coherent
        # TODO: check order_index is continuous
        geom = (
            self.cabletube_set.order_by("order_index")
            .annotate(
                offset_geom=Force3D(
                    OffsetCurve("tube__geom", "display_offset", Value("join=mitre"))
                )
            )
            .aggregate(geom=MakeLineAgg("offset_geom"))["geom"]
        )
        print(333, geom)
        self.geom = geom
        # cursor = connection.cursor()
        # print(connection.queries)
        # cursor.execute("SELECT * FROM azimuth_along_line")

    @transaction.atomic
    def save(self, **kwargs):
        if self._state.adding:
            self.compute_geom()
        super().save(**kwargs)


@register_oapif_viewset(crs=2056)
class Tube(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, blank=True
    )
    fake_id = models.UUIDField(default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    original_id = models.TextField(null=True, blank=True, editable=True)
    status = models.ForeignKey(
        StatusType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    diameter = models.IntegerField(
        default=None, null=True, blank=True, help_text="Diameter in mm"
    )
    cable_protection_type = models.ForeignKey(
        TubeCableProtectionType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    # TODO: this should not be editable, but switching prevent from seeing it in admin
    # TODO: this should not be nullable?
    geom = models.LineStringField(srid=2056, dim=3, null=True, blank=True)

    def compute_geom(self):
        # TODO: check geometry exists + is coherent
        # TODO: check order_index is continuous

        # TODO recalculate cables on change
        # TODO Z offset

        geom = (
            self.tubesection_set.order_by("order_index")
            .annotate(
                length=Length2d("section__geom"),
                offset_x_m=ExpressionWrapper(
                    Cast("offset_x", output_field=models.FloatField()) / 1000,
                    output_field=models.FloatField(),
                ),
                offset_z_m=ExpressionWrapper(
                    Cast("offset_z", output_field=models.FloatField()) / 1000,
                    output_field=models.FloatField(),
                ),
            )
            .annotate(
                planar_offset_fraction=ExpressionWrapper(
                    Least(0.3, 1.0 / F("length")), output_field=models.FloatField()
                )
            )
            .annotate(
                geom_reduced=LineSubstring(
                    "section__geom",
                    "planar_offset_fraction",
                    1 - F("planar_offset_fraction"),
                ),
                start_point=StartPoint("section__geom"),
                end_point=EndPoint("section__geom"),
            )
            .annotate(
                offset_geom_reduced=ProjectZOnLine(
                    OffsetCurve("geom_reduced", "offset_x_m", Value("join=mitre")),
                    "geom_reduced",
                    "offset_z_m",
                )
            )
            .annotate(
                offset_geom_full=MakeLine(
                    MakeLine("start_point", "offset_geom_reduced"), "end_point"
                )
            )
            .aggregate(geom=LineMerge(Union("offset_geom_full")))["geom"]
        )
        self.geom = geom

    @transaction.atomic
    def save(self, **kwargs):
        if self._state.adding:
            self.compute_geom()
        super().save(**kwargs)


@register_oapif_viewset(geom_field=None)
class TubeSection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    tube = models.ForeignKey(Tube, on_delete=models.CASCADE, null=False)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=False)
    order_index = models.IntegerField(default=0, null=False, blank=False)
    interpolated = models.BooleanField(default=False, null=False, blank=False)
    offset_x = models.IntegerField(null=False, blank=False, default=0)
    offset_z = models.IntegerField(null=False, blank=False, default=0)

    class Meta:
        ordering = ["order_index"]

    @transaction.atomic
    def save(self, **kwargs):
        super().save(**kwargs)
        self.tube.compute_geom()
        self.tube.save()


@register_oapif_viewset(geom_field=None)
class CableTube(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    tube = models.ForeignKey(Tube, on_delete=models.CASCADE)
    cable = models.ForeignKey(Cable, on_delete=models.CASCADE)
    order_index = models.IntegerField(default=0, null=False, blank=False)
    display_offset = models.IntegerField(default=0, null=False, blank=False)

    class Meta:
        ordering = ["order_index"]

    @transaction.atomic
    def save(self, **kwargs):
        if self._state.adding:
            do = CableTube.objects.filter(tube=self.tube).aggregate(
                do=Max("display_offset")
            )["do"]
            if do is None:
                do = -1
            self.display_offset = do + 1
        super().save(**kwargs)
        self.cable.compute_geom()
        self.cable.save()


@register_oapif_viewset(crs=2056)
class Station(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    original_id = models.TextField(null=True, editable=True)
    label = models.CharField(max_length=64, blank=True, null=True)
    geom = models.PointField(srid=2056, dim=3)


class Node(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)


class Reach(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    node_1 = models.ForeignKey(
        Node, related_name="node_1", blank=True, null=True, on_delete=models.SET_NULL
    )
    node_2 = models.ForeignKey(
        Node, related_name="node_2", blank=True, null=True, on_delete=models.SET_NULL
    )


class VirtualNode(Node):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)


class Switch(Reach):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)


class Terminal(Node):
    pass
