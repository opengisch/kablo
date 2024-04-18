import random
from math import cos, radians, sin

from django.db import connection
from django.test import TestCase, override_settings

from kablo.core.utils import wkt_from_line


class GeometryTestCase(TestCase):
    def setUp(self):
        pass

    @override_settings(DEBUG=True)
    def test_azimuth_along_line(self):

        x = 2508500
        y = 1152000

        line = [(x, y)]
        azimuths = [10, 40, 20, 100, 180, -90, -20, 10]
        for azimuth in azimuths:
            # make dist random to make the test more robust
            dist = random.randint(10, 100)
            x += dist * cos(radians(90 - azimuth))
            y += dist * sin(radians(90 - azimuth))
            line.append((x, y))

        geom_line_wkt = wkt_from_line(line)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT azimuth_along_line(ST_GeomFromText(%s))", [geom_line_wkt]
            )
            row = cursor.fetchone()[0]

        # expected azimuths are the mean of angles
        expected_azimuths = [10, 25, 30, 60, 140, -135, -55, -5, 10]

        self.assertEqual(row, expected_azimuths)
