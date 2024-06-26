import random
from math import cos, radians, sin

from django.contrib.gis.geos import LineString, MultiLineString
from django.test import TestCase, override_settings

from kablo.core.utils import wkt_from_multiline
from kablo.network.models import Cable, CableTube, Section, Track, Tube, TubeSection


class TrackSectionTestCase(TestCase):
    def setUp(self):
        pass

    # see https://stackoverflow.com/a/56773783/1548052
    @override_settings(DEBUG=True)
    def test_track_section_create_update(self):
        x = 2508500
        y = 1152000

        line = [(x + 10 * i, y + 10 * i) for i in range(5)]
        geom_line_wkt = wkt_from_multiline([line])
        fields = {"geom": geom_line_wkt}
        track = Track.objects.create(**fields)

        n_sections = 1
        for split_index in range(2, 4):
            mid_x = (line[split_index][0] + line[split_index + 1][0]) / 2
            mid_y = (line[split_index][1] + line[split_index + 1][1]) / 2
            split_line = [(mid_x, mid_y - 10), (mid_x, mid_y)]
            split_line_geom = LineString(split_line, srid=2056)

            qs = Section.objects.filter(track=track)

            self.assertEqual(qs.count(), n_sections)
            # self.assertEqual(sections[0].geom, track.geom)
            # self.assertEqual(track_sections[0].geom, GEOSGeometry(geom_line_wkt))
            # self.assertEqual(sections[0].geom.wkt, geom_line_wkt)

            track.split(split_line_geom)
            n_sections += 1

            self.assertEqual(qs.count(), n_sections)
            # self.assertEqual(sections[0].geom, track.geom)

    @override_settings(DEBUG=True)
    def test_tube_geom(self):
        x = 2508500
        y = 1152000

        tracks = []
        sections = []
        for t in range(1, 3):
            azimuths = [[10, 40, 20, 100, 60], [-90, -20, 10]]
            multiline = []
            for section_azimuths in azimuths:
                line = [(x, y, -10)]
                for azimuth in section_azimuths:
                    # make dist random to make the test more robust
                    dist = random.randint(8, 15)
                    x += dist * cos(radians(90 - azimuth))
                    y += dist * sin(radians(90 - azimuth))
                    line.append((x, y, 20))
                multiline.append(LineString(line, srid=2056))

            ml = MultiLineString(multiline, srid=2056)
            fields = {"geom": ml}
            track = Track.objects.create(**fields)
            for section in track.section_set.all():
                sections.append(section)

            tracks.append(track)

        tube = Tube.objects.create()

        i = 0
        for section in sections:
            offset_x = 100
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

    @override_settings(DEBUG=True)
    def test_section_tube_geom_merge(self):
        x = 2508500
        y = 1152000

        geom1 = MultiLineString(LineString((x, y, 0), (x + 10, y, 20), srid=2056))
        track1 = Track.objects.create(geom=geom1)
        section1 = track1.section_set.first()

        geom2 = MultiLineString(LineString((x, y, 0), (x - 10, y, 10), srid=2056))
        track2 = Track.objects.create(geom=geom2)
        section2 = track2.section_set.first()

        for offset_x in (0, 100):
            tube12 = Tube.objects.create()
            for i, section in enumerate(
                (
                    section1,
                    section2,
                )
            ):
                TubeSection.objects.create(
                    tube=tube12,
                    section=section,
                    order_index=i,
                    interpolated=False,
                    offset_x=offset_x,
                    offset_z=66,
                )

            tube1 = Tube.objects.create()
            TubeSection.objects.create(
                tube=tube1,
                section=section1,
                order_index=0,
                interpolated=False,
                offset_x=offset_x,
                offset_z=66,
            )

            tube2 = Tube.objects.create()
            TubeSection.objects.create(
                tube=tube2,
                section=section2,
                order_index=0,
                interpolated=False,
                offset_x=offset_x,
                offset_z=66,
            )

            for display_offset in (0, 1):
                cable12 = Cable.objects.create()
                for i, tube in enumerate((tube1, tube2)):
                    CableTube.objects.create(
                        tube=tube,
                        cable=cable12,
                        order_index=i,
                        display_offset=display_offset,
                    )
