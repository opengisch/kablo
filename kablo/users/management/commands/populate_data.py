import random
from math import cos, radians, sin
from typing import List, Tuple

from django.core.management.base import BaseCommand
from django.db import transaction

from kablo.core.utils import wkt_from_line, wkt_from_multiline
from kablo.editing.models import TrackSplit
from kablo.network.models import Section, Track, Tube, TubeSection


class Command(BaseCommand):
    help = "Populate db with testdata"

    def add_arguments(self, parser):
        parser.add_argument("-s", "--size", type=int, default=1000)

    @staticmethod
    def create_track(
        x: int, y: int, azimuths: List[List[int]], tracks_sections
    ) -> Track:
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
        tracks_sections.append([])
        for section in track.section_set.order_by("order_index").all():
            tracks_sections[-1].append(section)
        track.save()
        return track

    @staticmethod
    def create_tube(
        track_sections: List[List[Section]],
        track_section_indexes: List[Tuple[int, List[int]]],
        offset: int,
    ):
        tube = Tube.objects.create()
        i = 0
        for (track_idx, section_indexes) in track_section_indexes:
            for section_index in section_indexes:
                section = track_sections[track_idx][section_index]
                TubeSection.objects.create(
                    tube=tube,
                    section=section,
                    order_index=i,
                    interpolated=False,
                    offset_x=offset,
                    offset_z=0,
                )
                i += 1
        tube.save()

    @transaction.atomic
    def handle(self, *args, **options):
        """Populate db with testdata"""
        x = 2509600
        y = 1152000

        # list of tracks (track = list of sections => list of list of sections)
        tracks_sections = []

        tracks = []
        azimuths = [[10, 40, 20, 100, 50], [-30, -20, 10]]
        for track_idx in range(0, 3):
            track = self.create_track(x, y, azimuths, tracks_sections)
            (x, y, z) = track.geom.coords[-1][-1]
            tracks.append(track)

        (x, y, z) = tracks[1].geom.coords[-1][-1]
        azimuths = [[100, 120, 30, 100, 50], [-30, -20, 10]]
        track = self.create_track(x, y, azimuths, tracks_sections)
        tracks.append(track)

        tube_1_track_indexes = [
            (0, [0, 1]),
            (1, [0, 1]),
            (2, [0, 1]),
        ]
        self.create_tube(tracks_sections, tube_1_track_indexes, 50)

        tube_1_track_indexes = [
            (0, [0, 1]),
            (1, [0, 1]),
            (3, [0, 1]),
        ]
        self.create_tube(tracks_sections, tube_1_track_indexes, -100)

        # all layers neeed some data to be loaded in QGIS
        line = [(x - 1000 + 10 * i, y + 10 * i) for i in range(2)]
        geom_line_wkt = wkt_from_line(line, force3d=False)
        fields = {"geom": geom_line_wkt, "force_save": True}
        TrackSplit.objects.create(**fields)

        print(f"🤖 testdata added!")
