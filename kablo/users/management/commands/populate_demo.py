import json

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.db import transaction

from kablo.core.utils import import_arcsde_linestrings_to_geos
from kablo.network.models import Cable, Station, Track, Tube
from kablo.valuelist.models import CableTensionType, StatusType, TubeCableProtectionType


def import_stations(file):
    Station.objects.all().delete()
    with open(file, "r") as fd:
        data = json.load(fd)
        for feature in data["features"]:
            fields = {
                "geom": Point(feature["geometry"]["coordinates"]),
                "original_id": feature["properties"]["globalid"],
                "label": feature["properties"]["nummer"],
            }
            Station.objects.create(**fields)


def import_tracks(file):
    Track.objects.all().delete()
    with open(file, "r") as fd:
        data = json.load(fd)
        for feature in data["features"]:

            geom = import_arcsde_linestrings_to_geos(feature["geometry"])

            if geom:
                fields = {
                    "geom": geom,
                    "original_id": feature["properties"]["globalid"],
                }
                Track.objects.create(**fields)


def import_tubes(file):

    Tube.objects.all().delete()
    unknown_status = StatusType.objects.get(code=1)
    unknown_cable_protection_type = TubeCableProtectionType.objects.get(code=1)
    # TODO: log missing data as quality control
    with open(file, "r") as fd:
        data = json.load(fd)
        for feature in data["features"]:

            geom = import_arcsde_linestrings_to_geos(feature["geometry"])
            status = StatusType.objects.filter(
                code=feature["properties"]["status"]
            ).first()

            if not status:
                status = unknown_status

            cable_protection_type = TubeCableProtectionType.objects.filter(
                code=feature["properties"]["kabelschutz"]
            ).first()

            if not cable_protection_type:
                cable_protection_type = unknown_cable_protection_type

            if geom:
                fields = {
                    "status": status,
                    "cable_protection_type": cable_protection_type,
                    "geom": geom,
                    "original_id": feature["properties"]["globalid"],
                }

                Tube.objects.create(**fields)


def import_cables(file):
    Cable.objects.all().delete()
    unknown_tension_type = CableTensionType.objects.get(code=1)
    unknown_status = StatusType.objects.get(code=1)
    # TODO: log missing data as quality control
    with open(file, "r") as fd:
        data = json.load(fd)
        for feature in data["features"]:

            geom = import_arcsde_linestrings_to_geos(feature["geometry"])

            status = StatusType.objects.filter(
                code=feature["properties"]["status"]
            ).first()

            if not status:
                status = unknown_status

            tension_type = CableTensionType.objects.filter(
                code=feature["properties"]["status"]
            ).first()

            if not tension_type:
                tension_type = unknown_tension_type

            if geom:
                fields = {
                    "tension": tension_type,
                    "status": status,
                    "geom": geom,
                    "original_id": feature["properties"]["globalid"],
                }
                Cable.objects.create(**fields)


def import_tube_cable_relations(file):
    # Set cable-tube m2m relation
    print(f"🤖 ...Setting tube_cable m2m relations...this might take some time...")
    with open(file, "r") as fd:
        data = json.load(fd)

        for feature in data:
            cable = Cable.objects.filter(original_id=feature["kabel_ref"]).first()
            tube = Tube.objects.filter(original_id=feature["rohr_ref"]).first()
            if cable and tube:
                tube.cables.add(cable)


class Command(BaseCommand):
    help = "Populate db with demo data"

    @transaction.atomic
    def handle(self, *args, **options):
        """Populate db with testdata"""

        import_tracks("/kablo/demo/data/dbo.ele_trasse.geojson")
        print(f"🤖 demo tracks added!")
        # Tubes must be imported before cables as the relation is set
        # after cable creation
        import_tubes("/kablo/demo/data/dbo.ele_rohr.geojson")
        print(f"🤖 demo tubes added!")

        import_cables("/kablo/demo/data/dbo.ele_kabel.geojson")
        print(f"🤖 demo cables added!")

        import_stations("/kablo/demo/data/dbo.ele_station.geojson")
        print(f"🤖 demo stations added!")

        # Must be executed after tubes and cables import
        import_tube_cable_relations("/kablo/demo/data/dbo.eler_rohr_kabel.json")
        print(f"🤖 tubes-cables relations added!")
