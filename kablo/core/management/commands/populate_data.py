from django.core.management.base import BaseCommand
from django.db import transaction

from kablo.core.utils import wkt_from_line
from kablo.network.models import Track


class Command(BaseCommand):
    help = "Populate db with testdata"

    def add_arguments(self, parser):
        parser.add_argument("-s", "--size", type=int, default=1000)

    @transaction.atomic
    def handle(self, *args, **options):
        """Populate db with testdata"""
        x = 2508500
        y = 1152000
        line = [(x + 10 * i, y + 10 * i) for i in range(5)]
        geom_line_wkt = wkt_from_line(line)

        fields = {"geom": geom_line_wkt}
        Track.objects.create(**fields)

        # Call 'update_data' to update computed properties
        # call_command("updatedata")
        print(f"🤖 testdata added!")
