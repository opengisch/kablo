import random
import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from pyinstrument import Profiler

from kablo.apps.network.models import Cable, Track, TrackSection, Tube

profiler = Profiler()


class Command(BaseCommand):
    help = "Populate db with testdata"

    def add_arguments(self, parser):
        parser.add_argument("-s", "--size", type=int, default=100)

    @transaction.atomic
    def handle(self, *args, **options):
        """Populate db with testdata"""

        if settings.ENV.upper() != "DEV":
            self.stdout.write(
                self.style.ERROR("Les fixtures ne peuvent être exécutés qu'en DEV")
            )
            sys.exit()

        tracks_number = options["size"]

        Track.objects.all().delete()
        TrackSection.objects.all().delete()
        Tube.objects.all().delete()
        Cable.objects.all().delete()

        linetring_vertex_number = 100
        tracks_to_create = []
        for j in range(tracks_number):
            x = 2508500
            y = 1152000
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

        print(f"🤖 {tracks_number} Tracks testdata added!")

        # ONLY FOR TEST, dont' try this at home it WILL hurt your db BADLY
        profiler.start()
        for track_section in Track.get_sections(tracks):
            Tube.objects.create().track_sections.add(track_section)

        for tube in Tube.objects.all():
            Cable.objects.create().tubes.add(tube)
        profiler.stop()
        profiler.print()
