import uuid
from math import atan2, cos, degrees, radians, sin

from django.contrib.gis.db import models
from django.contrib.gis.db.models.aggregates import Union
from django.contrib.gis.geos import LineString
from django.contrib.postgres.fields import ArrayField
from django.db import transaction
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
    geom = models.MultiLineStringField(srid=2056, dim=3, null=True)


@register_oapif_viewset(crs=2056)
class Tube(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_id = models.TextField(null=True, editable=True)
    status = models.ForeignKey(
        StatusType,
        null=True,
        on_delete=models.SET_NULL,
    )
    cable_protection_type = models.ForeignKey(
        TubeCableProtectionType,
        null=True,
        on_delete=models.SET_NULL,
    )
    cables = models.ManyToManyField(Cable)
    # TODO: this should not be editable, but switching prevent from seeing it in admin
    # TODO: this should not be nullable?
    geom = models.LineStringField(srid=2056, dim=3, null=True)
    sections = models.ManyToManyField(Section, through="TubeSection")

    @transaction.atomic
    def save(self, **kwargs):
        # recalculate geom
        # TODO: check geometry exists + is coherent
        # TODO: check order_index is continuous

        # combined_geom = self.tubesection_set.order_by("order_index").annotate(combined_geom=Union('section__geom')).annotate(AzimuthAlongLine('combined_geom'))
        # combined_geom = self.tubesection_set.order_by("order_index").aggregate(combined_geom=Union('section__geom'))['combined_geom']
        # print(combined_geom)

        tube_line = []
        last_azimuth = None
        last_offset_x = None
        last_offset_z = None

        for tube_section in (
            self.tubesection_set.order_by("order_index")
            .annotate(azimuths=AzimuthAlongLine("section__geom"))
            .all()
        ):

            # TODO: this works when the tube already exists (i.e. we are adding section after it was created and saved)
            # TODO: there is probably a way to make this qs outside of the loop for optimization

            section = tube_section.section

            offset_x_set = tube_section.offset_x
            offset_z_set = tube_section.offset_z

            assert len(tube_section.azimuths) == len(section.geom.coords)
            if tube_section.order_index == 0:
                assert len(offset_x_set) == len(section.geom.coords)
                assert len(offset_z_set) == len(section.geom.coords)
            else:
                assert len(offset_x_set) == len(section.geom.coords) - 1
                assert len(offset_z_set) == len(section.geom.coords) - 1
                offset_x_set = [last_offset_x] + offset_x_set
                offset_z_set = [last_offset_z] + offset_z_set

            first_vertex_in_section = True
            for (point, azimuth, offset_x, offset_z) in zip(
                section.geom.coords,
                tube_section.azimuths,
                offset_x_set,
                offset_z_set,
            ):
                # calculate mean of angles on section join, recalculate previous point and go to next one
                if first_vertex_in_section and last_azimuth:
                    # TODO: we might want to check that the coordinates are exactly the same (but it might be checked somehwere else: in geometry integrity checks?)

                    az1 = radians(last_azimuth)
                    az2 = radians(azimuth)
                    azimuth = degrees(
                        atan2((sin(az1) + sin(az2)) / 2, (cos(az1) + cos(az2)) / 2)
                    )

                # segment_direction_angle = 90 - azimuth
                # orthogonal_direction = segment_direction + 90
                x = point[0] + cos(radians(90 - azimuth + 90)) * offset_x / 1000
                y = point[1] + sin(radians(90 - azimuth + 90)) * offset_x / 1000
                z = point[2] + offset_z

                if first_vertex_in_section and last_azimuth:
                    tube_line[-1] = (x, y, z)

                else:
                    tube_line.append((x, y, z))

                first_vertex_in_section = False
                last_azimuth = azimuth
                last_offset_x = offset_x
                last_offset_z = offset_z

        if len(tube_line) > 0:
            self.geom = LineString(tube_line)

        super().save(**kwargs)


class TubeSection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tube = models.ForeignKey(Tube, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    order_index = models.IntegerField(default=1)
    interpolated = models.BooleanField(default=False, null=False, blank=False)
    # TODO check data integrity: len(offsets) = n_vertex if order_index = 0, n_vertex-1 otherwise
    offset_x = ArrayField(models.IntegerField(null=False, blank=False, default=0))
    # TODO: potentially we want an absolute Z rather than an offset
    offset_z = ArrayField(models.IntegerField(null=False, blank=False, default=0))

    class Meta:
        ordering = ["order_index"]

    @transaction.atomic
    def save(self, **kwargs):
        n_vertices = len(self.section.geom.coords)
        n_offset = n_vertices - int(self.order_index > 0)
        if type(self.offset_x) != list:
            self.offset_x = n_offset * [self.offset_x]
        elif len(self.offset_x) != n_offset:
            # TODO raise error
            pass
        if type(self.offset_z) != list:
            self.offset_z = n_offset * [self.offset_z]
        elif len(self.offset_z) != n_offset:
            # TODO raise error
            pass

        super().save(**kwargs)

    # TODO: recalculate tube geom when changed


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
