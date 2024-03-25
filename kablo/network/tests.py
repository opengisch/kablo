from django.contrib.gis.geos import LineString
from django.test import TestCase, override_settings

from kablo.core.utils import wkt_from_multiline
from kablo.network.models import Section, Track


class TrackSectionTestCase(TestCase):
    def setUp(self):
        pass

    # see https://stackoverflow.com/a/56773783/1548052
    @override_settings(DEBUG=True)
    def test_track_section_create_update(self):
        x = 2508500
        y = 1152000

        line = [(x + 10 * i, y + 10 * i) for i in range(5)]
        geom_line_wkt = wkt_from_multiline(line)
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
