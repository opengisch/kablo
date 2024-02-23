import random
import sys

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from pyinstrument import Profiler

from kablo.apps.network.models import Track, TrackSection

profiler = Profiler()


class Command(BaseCommand):
    help = "Populate db with testdata"

    def add_arguments(self, parser):
        parser.add_argument("-s", "--size", type=int, default=1000)

    @transaction.atomic
    def handle(self, *args, **options):
        """Populate db with testdata"""

        if settings.ENV.upper() != "DEV":
            self.stdout.write(
                self.style.ERROR("Les fixtures ne peuvent être exécutés qu'en DEV")
            )
            sys.exit()

        # TODO: reset whole DB one shot ?
        User = get_user_model()
        User.objects.all().delete()
        Track.objects.all().delete()
        TrackSection.objects.all().delete()
        # Create superuser
        User.objects.create_user(
            email=None,
            first_name="admin",
            last_name="admin",
            username="admin",
            password="admin",
            is_staff=True,
            is_superuser=True,
        )

        print(f"🤖 superuser admin/admin created")

        tracks_number = 10000
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
        Track.objects.bulk_save_tracks(tracks_to_create)
        profiler.stop()
        profiler.print()
        print(f"🤖 {tracks_number} Tracks testdata added!")
