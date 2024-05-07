import json

from django.core.management.base import BaseCommand
from django.db import transaction

from kablo.valuelist.models import CableTensionType, StatusType, TubeCableProtectionType


class Command(BaseCommand):
    help = "Populate db with testdata"

    @transaction.atomic
    def handle(self, *args, **options):

        base_dir = "/kablo/kablo/valuelist/management/data/"

        value_lists = {
            "status": {"model": StatusType, "file": "dbo.eles_status.json"},
            "cable_protection": {
                "model": TubeCableProtectionType,
                "file": "dbo.eles_kabelschutz_rohr.json",
            },
            "cable_tension": {
                "model": CableTensionType,
                "file": "dbo.eles_spannung.json",
            },
        }

        for key in value_lists:
            value_lists[key]["model"].objects.all().delete()
            with open(f'{base_dir}/{value_lists[key]["file"]}') as fd:
                data = json.load(fd)
                for feature in data:
                    del feature["json_featuretype"]
                    del feature["_feature_type"]
                    value_lists[key]["model"].objects.create(**feature)

            print(f"🤖 Values added for list {key}!")
