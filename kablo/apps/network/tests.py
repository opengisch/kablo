from django.test import TestCase

from .models import Track, TrackSection


class TrackSectionTestCase(TestCase):
    def setUp(self):
        pass

    def test_track_section_create_update(self):
        x = 2508500
        y = 1152000
        line_x = [x + 10 * i for i in range(5)]
        line_y = [y + 10 * i for i in range(5)]

        geom_line_wkt = ", ".join([f"{x} {y}" for x, y in zip(line_x, line_y)])
        geom_line_wkt = f"LINESTRING ({geom_line_wkt})"

        fields = {"geom": geom_line_wkt}

        track = Track.objects.create_track(**fields)
        track_sections = TrackSection.objects.filter(track=track)

        self.assertEqual(len(track_sections), 1)
        self.assertEqual(track_sections[0].geom, track.geom)
        # self.assertEqual(track_sections[0].geom, GEOSGeometry(geom_line_wkt))
        self.assertEqual(track_sections[0].geom.wkt, geom_line_wkt)
