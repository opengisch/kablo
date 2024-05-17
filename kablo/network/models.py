import uuid
from math import cos, radians, sin

from django.contrib.gis.db import models
from django.contrib.gis.db.models.aggregates import Union
from django.contrib.gis.geos import LineString
from django.db import transaction
from django.db.models import Max
from django_oapif.decorators import register_oapif_viewset

from kablo.core.geometry import AzimuthAlongLine, Intersects, SplitLine
from kablo.valuelist.models import CableTensionType, StatusType, TubeCableProtectionType


class NetworkNode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    geom = models.PointField(srid=2056, dim=3)


@register_oapif_viewset(crs=2056)
class Track(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
        # TODO: if holes, create junction (e.g. within station)
        self.geom = self.cabletube_set.order_by("order_index").aggregate(
            geom=Union("tube__geom")
        )["geom"]

    @transaction.atomic
    def save(self, **kwargs):
        if self._state.adding:
            self.compute_geom()
        super().save(**kwargs)


@register_oapif_viewset(crs=2056)
class Tube(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_id = models.TextField(null=True, editable=True)
    status = models.ForeignKey(
        StatusType,
        null=True,
        on_delete=models.SET_NULL,
    )
    diameter = models.IntegerField(
        default=None, null=True, blank=True, help_text="Diameter in mm"
    )
    cable_protection_type = models.ForeignKey(
        TubeCableProtectionType,
        null=True,
        on_delete=models.SET_NULL,
    )
    # TODO: this should not be editable, but switching prevent from seeing it in admin
    # TODO: this should not be nullable?
    geom = models.LineStringField(srid=2056, dim=3, null=True)
    sections = models.ManyToManyField(Section, through="TubeSection")

    def compute_geom(self):
        # TODO: check geometry exists + is coherent
        # TODO: check order_index is continuous
        tube_line = []

        qs = self.tubesection_set.order_by("order_index").annotate(
            azimuths=AzimuthAlongLine("section__geom")
        )

        max_order_index = qs.aggregate(max_order_index=Max("order_index"))[
            "max_order_index"
        ]
        first_vertex = True

        for tube_section in qs.all():
            # TODO: this works when the tube already exists (i.e. we are adding section after it was created and saved)

            last_section = tube_section.order_index == max_order_index
            first_vertex_in_section = True

            coords = tube_section.section.geom.coords
            if tube_section.reversed:
                coords.reverse()

            for i, (point, azimuth) in enumerate(zip(coords, tube_section.azimuths)):
                planimetric_offset_x = 0
                planimetric_offset_y = 0

                last_vertex_in_section = i == len(tube_section.section.geom.coords) - 1
                last_vertex = last_section and last_vertex_in_section

                # In case of different start and ending offset,
                # we take the mean at intermediate vertex for now
                # TODO: do a linear interpolation
                offset_x = tube_section.offset_x
                if tube_section.offset_x_2:
                    offset_x = (tube_section.offset_x + tube_section.offset_x_2) / 2
                offset_z = tube_section.offset_z
                if tube_section.offset_z_2:
                    offset_z = (tube_section.offset_z + tube_section.offset_z_2) / 2

                if first_vertex:
                    tube_line.append((point[0], point[1], point[2]))
                    first_vertex = False

                if first_vertex_in_section:
                    # tube offset starts at a certain gap from first vertex
                    # TODO: define app setting for offset + possibility to override per TubeSection (start + end)
                    # planimetric offset is to start the offset away from the node to improve visualisation
                    planimetric_offset_x = 0.5 * cos(radians(90 - azimuth))
                    planimetric_offset_y = 0.5 * sin(radians(90 - azimuth))
                    first_vertex_in_section = False
                    offset_x = tube_section.offset_x
                    offset_z = tube_section.offset_z

                if last_vertex_in_section:
                    # planimetric offset is to start the offset away from the node to improve visualisation
                    planimetric_offset_x = 0.5 * cos(radians(90 - azimuth + 180))
                    planimetric_offset_y = 0.5 * sin(radians(90 - azimuth + 180))
                    offset_x = tube_section.offset_x_2 or tube_section.offset_x
                    offset_z = tube_section.offset_z_2 or tube_section.offset_z

                # segment_direction_angle = 90 - azimuth
                # orthogonal_direction = segment_direction + 90
                od = radians(90 - azimuth + 90)
                x = point[0] + planimetric_offset_x + cos(od) * offset_x / 1000
                y = point[1] + planimetric_offset_y + sin(od) * offset_x / 1000
                z = point[2] + offset_z  # TODO: absolute vs relative Z

                tube_line.append((x, y, z))

                if last_vertex:
                    tube_line.append((point[0], point[1], point[2]))

        if len(tube_line) > 0:
            self.geom = LineString(tube_line)

    @transaction.atomic
    def save(self, **kwargs):
        if self._state.adding:
            self.compute_geom()
        super().save(**kwargs)


@register_oapif_viewset(geom_field=None)
class TubeSection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tube = models.ForeignKey(Tube, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    order_index = models.IntegerField(default=1)
    reversed = models.BooleanField(default=False, null=False, blank=False)
    interpolated = models.BooleanField(default=False, null=False, blank=False)
    offset_x = models.IntegerField(null=False, blank=False, default=0)
    offset_z = models.IntegerField(null=False, blank=False, default=0)
    offset_x_2 = models.IntegerField(
        null=True,
        blank=True,
        default=None,
        help_text="Optional x end offset (if different from from start)",
    )
    offset_z_2 = models.IntegerField(
        null=True,
        blank=True,
        default=None,
        help_text="Optional z end offset (if different from from start)",
    )

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
    tube = models.ForeignKey(Tube, on_delete=models.CASCADE)
    cable = models.ForeignKey(Cable, on_delete=models.CASCADE)
    order_index = models.IntegerField(default=0)

    class Meta:
        ordering = ["order_index"]

    @transaction.atomic
    def save(self, **kwargs):
        super().save(**kwargs)
        self.cable.compute_geom()
        self.cable.save()


@register_oapif_viewset(crs=2056)
class Station(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_id = models.TextField(null=True, editable=True)
    label = models.CharField(max_length=64, blank=True, null=True)
    geom = models.PointField(srid=2056, dim=3)


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


class VirtualNode(Node):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)


class Switch(Reach):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)


class Terminal(Node):
    pass
