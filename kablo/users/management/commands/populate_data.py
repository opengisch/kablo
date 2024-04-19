import random
from math import cos, radians, sin

from django.core.management.base import BaseCommand
from django.db import transaction

from kablo.core.utils import wkt_from_line, wkt_from_multiline
from kablo.editing.models import TrackSplit
from kablo.network.models import Track, Tube, TubeSection


class Command(BaseCommand):
    help = "Populate db with testdata"

    def add_arguments(self, parser):
        parser.add_argument("-s", "--size", type=int, default=1000)

    @transaction.atomic
    def handle(self, *args, **options):
        """Populate db with testdata"""
        x = 2508200
        y = 1152000

        tracks = []
        sections = []
        for t in range(1, 3):
            azimuths = [[10, 40, 20, 100, 50], [-30, -20, 10]]
            multiline = []
            for section_azimuths in azimuths:
                line = [(x, y)]
                for azimuth in section_azimuths:
                    # make dist random to make the test more robust
                    dist = random.randint(5, 15)
                    x += dist * cos(radians(90 - azimuth))
                    y += dist * sin(radians(90 - azimuth))
                    line.append((x, y))
                multiline.append(line)

            geom_line_wkt = wkt_from_multiline(multiline)
            fields = {"geom": geom_line_wkt}
            track = Track.objects.create(**fields)
            for section in track.section_set.order_by("order_index").all():
                sections.append(section)
            tracks.append(track)

        tube = Tube.objects.create()
        i = 0
        for section in sections:
            n_vertices = len(section.geom.coords)
            offset_x = [100] * n_vertices
            offset_z = 0
            TubeSection.objects.create(
                tube=tube,
                section=section,
                order_index=i,
                interpolated=False,
                offset_x=offset_x,
                offset_z=offset_z,
            )
            i += 1

        tube.save()

        # all layers neeed some data to be loaded in QGIS
        line = [(x - 1000 + 10 * i, y + 10 * i) for i in range(2)]
        geom_line_wkt = wkt_from_line(line, force3d=False)
        fields = {"geom": geom_line_wkt, "force_save": True}
        TrackSplit.objects.create(**fields)

        print(f"🤖 testdata added!")
