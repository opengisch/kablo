import json
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.gis.geos import Point

from kablo.core.utils import wkt_from_line
from kablo.network.models import Track, Station, Tube, Cable, StatusType, CableTensionType, TubeCableProtectionType


def import_value_lists():

    base_dir = "/kablo/kablo/core/management/data/core_value_lists_data"

    value_lists = {
        "status":{"model":StatusType, "file": "status.json"},
        "cable_protection":{"model":TubeCableProtectionType, "file": "cable_protection.json"},
        "cable_tension":{"model":CableTensionType, "file": "cable_tension.json"},
    }

    for key in value_lists:
        value_lists[key]["model"].objects.all().delete()
        with open(f'{base_dir}/{value_lists[key]["file"]}', 'r') as fd:
            data = json.load(fd)
            for feature in data:
                del feature["json_featuretype"]
                value_lists[key]["model"].objects.create(**feature)
        
        print(f"🤖 Values added for list {key}!")

def import_stations(file):
    Station.objects.all().delete()
    with open(file, 'r') as fd:
        data = json.load(fd)
        for feature in data['features']:
            fields = {
                "geom": Point(feature["geometry"]["coordinates"]),
                "original_uuid": feature["properties"]["globalid"],
            }
            Station.objects.create(**fields)

def import_tracks(file):
    Track.objects.all().delete()
    with open(file, 'r') as fd:
        data = json.load(fd)
        for feature in data['features']:
                    
            fields = {
                "geom": wkt_from_line(feature["geometry"]["coordinates"]),
                "original_uuid": feature["properties"]["globalid"]
            }
            Track.objects.create(**fields)

def import_tubes(file):
 
    Tube.objects.all().delete()
    with open(file, 'r') as fd:
        data = json.load(fd)
        for feature in data['features']:

            status = StatusType.objects.filter(code=feature["properties"]["status"]).first()
          
            if not status:
                status = StatusType.objects.get(code=1)

            cable_protection_type = TubeCableProtectionType.objects.get(code=feature["properties"]["kabelschutz"])

            if not cable_protection_type:
                cable_protection_type = TubeCableProtectionType.objects.get(code=1)

            fields = {
                "status": StatusType.objects.get(code=feature["properties"]["status"]),
                "cable_protection_type": TubeCableProtectionType.objects.get(code=feature["properties"]["kabelschutz"]),
                "geom": wkt_from_line(feature["geometry"]["coordinates"]),
                "original_uuid": feature["properties"]["globalid"]
            }

            Tube.objects.create(**fields)


def import_cables(file):
    Cable.objects.all().delete()
    with open(file, 'r') as fd:
        data = json.load(fd)
        for feature in data['features']:
                    
            fields = {
                "tension": CableTensionType.objects.get(code=feature["properties"]["status"]),
                "status": StatusType.objects.get(code=feature["properties"]["status"]),
                "geom": wkt_from_line(feature["geometry"]["coordinates"]),
                "original_uuid": feature["properties"]["globalid"]
            }
            Cable.objects.create(**fields)

    # Set cable-tube m2m relation
    with open('/kablo/demo/data/tube_cable_relation.json', 'r') as fd:
        data = json.load(fd)

        for feature in data:
            cable = Cable.objects.filter(original_uuid=feature["KABEL_REF"]).first()
            tube = Tube.objects.filter(original_uuid=feature["ROHR_REF"]).first()
            if cable and tube:
                cable.tubes.add(tube)


class Command(BaseCommand):
    help = "Populate db with demo data"

    def add_arguments(self, parser):
        parser.add_argument("-s", "--size", type=int, default=1000)

    @transaction.atomic
    def handle(self, *args, **options):
        """Populate db with testdata"""

        # Value lists must be added before anything else
        import_value_lists()
        print(f"🤖 Value types added!")

        import_tracks('/kablo/demo/data/dbo.ele_trasse.geojson')
        print(f"🤖 demo tracks added!")
        # Tubes must be imported before cables as the relation is set
        # after cable creation
        import_tubes('/kablo/demo/data/dbo.ele_rohr.geojson')
        print(f"🤖 demo tubes added!")

        import_cables('/kablo/demo/data/dbo.ele_kabel.geojson')
        print(f"🤖 demo cables added!")

        import_stations('/kablo/demo/data/dbo.ele_station.geojson')
        print(f"🤖 demo stations added!")
