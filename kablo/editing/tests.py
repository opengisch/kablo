from django.contrib.gis.geos import LineString
from django.test import TestCase, override_settings

from kablo.core.utils import wkt_from_line
from kablo.editing.models import TrackSplit
from kablo.network.models import Section, Track


class TrackSplitTestCase(TestCase):
    def setUp(self):
        pass

    @override_settings(DEBUG=True)
    def test_track_split(self):
        x = 2508500
        y = 1152000

        line = [(x + 10 * i, y + 10 * i) for i in range(5)]
        geom_line_wkt = wkt_from_line(line)

        mid_x = (line[2][0] + line[3][0]) / 2
        mid_y = (line[2][1] + line[3][1]) / 2
        split_line = [(mid_x, mid_y - 10), (mid_x, mid_y)]
        split_line_geom = LineString(split_line, srid=2056)

        fields = {"geom": geom_line_wkt}

        track = Track.objects.create(**fields)

        sections = Section.objects.filter(track=track)
        self.assertEqual(len(sections), 1)

        TrackSplit.objects.create(geom=split_line_geom, track=track)

        sections = Section.objects.filter(track=track)
        self.assertEqual(len(sections), 2)
