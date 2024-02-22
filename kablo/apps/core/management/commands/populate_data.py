import random

from django.core.management.base import BaseCommand
from django.db import transaction

from kablo.apps.network.models import Track


class Command(BaseCommand):
    help = "Populate db with testdata"

    def add_arguments(self, parser):
        parser.add_argument("-s", "--size", type=int, default=1000)

    @transaction.atomic
    def handle(self, *args, **options):
        """Populate db with testdata"""
        tracks = []

        x = 2508500
        y = 1152000
        line_x = []
        line_y = []
        for i in range(5):
            x += random.randint(1, 5)
            y += random.randint(1, 5)
            line_x.append(x)
            line_y.append(y)

        geom_line_wkt = ",".join([f"{x} {y}" for x, y in zip(line_x, line_y)])
        geom_line_wkt = f"LineString({geom_line_wkt})"

        fields = {"geom": geom_line_wkt}
        track = Track(**fields)
        tracks.append(track)

        # Create objects in batches
        Track.objects.bulk_create(tracks, batch_size=10000)

        # Call 'update_data' to update computed properties
        # call_command("updatedata")
        print(f"🤖 testdata added!")
