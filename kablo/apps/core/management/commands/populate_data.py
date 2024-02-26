import math
import random
import sys

from django.core.management.base import BaseCommand
from django.db import transaction
from pyinstrument import Profiler

from kablo.apps.network.models import Cable, Track, TrackSection, Tube

from .functions import *

profiler = Profiler()


class Command(BaseCommand):
    help = "Populate db with testdata"

    def add_arguments(self, parser):
        parser.add_argument("-s", "--size", type=int, default=100)

    @transaction.atomic
    def handle(self, *args, **options):
        """Populate db with testdata"""

        confirm_reset_data(sys)

        size = options["size"]

        Track.objects.all().delete()
        TrackSection.objects.all().delete()
        Tube.objects.all().delete()
        Cable.objects.all().delete()

        linetring_vertex_number = 100
        tracks_to_create = []
        x_start = 2508500
        y_start = 1152000
        step = 100
        magnitude = math.ceil(math.sqrt(size))

        for dx in range(magnitude):
            for dy in range(magnitude):
                x = x_start + dx * step
                y = y_start + dy * step
                line_x = []
                line_y = []
                for i in range(linetring_vertex_number):
                    x += random.randint(1, 5)
                    y += random.randint(1, 5)
                    line_x.append(x)
                    line_y.append(y)

                geom_line_wkt = ",".join([f"{x} {y}" for x, y in zip(line_x, line_y)])
                geom_line_wkt = f"LineString({geom_line_wkt})"
                tracks_to_create.append(Track(geom=geom_line_wkt))

        profiler.start()
        # Create Tracks in DB
        tracks = Track.objects.bulk_save_tracks(tracks_to_create)
        profiler.stop()
        profiler.print()

        sys.stdout.write(f"🤖 {size} Tracks testdata added!")

        # ONLY FOR TEST, dont' try this at home it WILL hurt your db BADLY
        profiler.start()
        for track_section in Track.get_sections(tracks):
            Tube.objects.create().track_sections.add(track_section)

        for tube in Tube.objects.all():
            Cable.objects.create().tubes.add(tube)
        profiler.stop()
        profiler.print()
