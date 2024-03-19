from django.contrib.gis.geos import LineString
from django.test import TestCase, override_settings

from .models import Section, Track


class TrackSectionTestCase(TestCase):
    def setUp(self):
        pass

    @staticmethod
    def wkt_from_line(line: list[tuple[float, float]]) -> str:
        geom_line_wkt = ", ".join([f"{x} {y}" for (x, y) in line])
        return f"MULTILINESTRING (({geom_line_wkt}))"

    # see https://stackoverflow.com/a/56773783/1548052
    @override_settings(DEBUG=True)
    def test_track_section_create_update(self):
        x = 2508500
        y = 1152000

        line = [(x + 10 * i, y + 10 * i) for i in range(5)]
        geom_line_wkt = self.wkt_from_line(line)

        mid_x = (line[2][0] + line[3][0]) / 2
        mid_y = (line[2][1] + line[3][1]) / 2
        split_line = [(mid_x, mid_y - 10), (mid_x, mid_y)]
        split_line_geom = LineString(split_line, srid=2056)

        fields = {"geom": geom_line_wkt}

        track = Track.objects.create(**fields)
        sections = Section.objects.filter(track=track)

        self.assertEqual(len(sections), 1)
        # self.assertEqual(sections[0].geom, track.geom)
        # self.assertEqual(track_sections[0].geom, GEOSGeometry(geom_line_wkt))
        # self.assertEqual(sections[0].geom.wkt, geom_line_wkt)

        track.split(split_line_geom)
        sections = Section.objects.filter(track=track)

        self.assertEqual(len(sections), 2)
        # self.assertEqual(sections[0].geom, track.geom)
