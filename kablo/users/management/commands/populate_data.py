import random
from math import cos, radians, sin

from django.core.management.base import BaseCommand
from django.db import transaction

from kablo.core.utils import wkt_from_line, wkt_from_multiline
from kablo.editing.models import TrackSplit
from kablo.network.models import Cable, CableTube, Section, Track, Tube, TubeSection


class Command(BaseCommand):
    help = "Populate db with testdata"

    def add_arguments(self, parser):
        parser.add_argument("-s", "--size", type=int, default=1000)

    @staticmethod
    def create_track(
        x: float, y: float, start_azimuth: int, azimuths: list[list[int]]
    ) -> (Track, list[Section]):
        multiline = []
        for section_azimuths in azimuths:
            line = [(x, y)]
            for azimuth in section_azimuths:
                # make dist random to make the test more robust
                dist = random.randint(5, 15)
                x += dist * cos(radians(start_azimuth + azimuth))
                y += dist * sin(radians(start_azimuth + azimuth))
                line.append((x, y))
            multiline.append(line)

        geom_line_wkt = wkt_from_multiline(multiline)
        fields = {"geom": geom_line_wkt}
        track = Track.objects.create(**fields)
        tracks_sections = []
        for section in track.section_set.order_by("order_index").all():
            tracks_sections.append(section)
        track.save()
        return track, tracks_sections

    @staticmethod
    def create_tube(
        track_sections: list[list[Section]],
        track_section_indexes: list[tuple[int, list[int]]],
        offset: int,
    ):
        # TODO: fix offset
        tube = Tube.objects.create(diameter=10 * random.randint(8, 25))
        i = 0
        for (track_idx, section_indexes) in track_section_indexes:
            for section_index in section_indexes:
                section = track_sections[track_idx][section_index]
                TubeSection.objects.create(
                    tube=tube,
                    section=section,
                    order_index=i,
                    interpolated=False,
                    offset_x=100 * random.randint(-4, 4),
                    offset_z=100 * random.randint(-1, 1),
                    # offset_x_2=100 * random.randint(-4, 4 ),
                )
                i += 1
        tube.save()
        return tube

    @staticmethod
    def create_cable(tubes: list[Tube]):
        # TODO: fix offset
        cable = Cable.objects.create()
        i = 0
        for tube in tubes:
            CableTube.objects.create(
                tube=tube,
                cable=cable,
                order_index=i,
            )
            i += 1
        cable.save()
        return cable

    @transaction.atomic
    def handle(self, *args, **options):
        """Populate db with testdata"""
        # list of tracks (track = list of sections => list of list of sections)
        azimuth_track_sections = []
        tubes = []

        for start_azimuth in range(0, 360, 90):
            x = 2516800
            y = 1152200

            azimuths = [[10, 40, 20, 100, 50], [-30, -20, 10]]

            azimuth_track_sections.append([])

            for track_idx in range(0, 3):
                (track, sections) = self.create_track(x, y, start_azimuth, azimuths)
                (x, y, z) = track.geom.coords[-1][-1]
                azimuth_track_sections[-1].append(sections)

            (x, y, z) = azimuth_track_sections[-1][1][1].geom.coords[-1]
            azimuths = [[120, 120, 30, 100, 50], [-30, -20, 10]]
            (track, sections) = self.create_track(x, y, start_azimuth, azimuths)
            azimuth_track_sections[-1].append(sections)

            tube_1_track_indexes = [
                (0, [0, 1]),
                (1, [0, 1]),
                (2, [0, 1]),
            ]
            for i in range(3):
                tubes.append(
                    self.create_tube(
                        azimuth_track_sections[-1], tube_1_track_indexes, 50
                    )
                )

            tube_2_track_indexes = [
                (0, [0, 1]),
                (1, [0, 1]),
                (3, [0, 1]),
            ]
            for i in range(3):
                tubes.append(
                    self.create_tube(
                        azimuth_track_sections[-1], tube_2_track_indexes, -100
                    )
                )

        self.create_cable([tubes[0]])
        self.create_cable([tubes[0]])
        self.create_cable([tubes[0]])
        self.create_cable([tubes[0]])
        self.create_cable([tubes[0]])
        self.create_cable([tubes[0]])
        self.create_cable([tubes[0]])

        # all layers need some data to be loaded in QGIS
        line = [(x - 1000 + 10 * i, y + 10 * i) for i in range(2)]
        geom_line_wkt = wkt_from_line(line, force3d=False)
        fields = {"geom": geom_line_wkt, "force_save": True}
        TrackSplit.objects.create(**fields)

        print(f"🤖 testdata added!")
