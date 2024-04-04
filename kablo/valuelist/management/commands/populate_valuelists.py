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
            "status": {"model": StatusType, "file": "status.json"},
            "cable_protection": {
                "model": TubeCableProtectionType,
                "file": "cable_protection.json",
            },
            "cable_tension": {"model": CableTensionType, "file": "cable_tension.json"},
        }

        for key in value_lists:
            value_lists[key]["model"].objects.all().delete()
            with open(f'{base_dir}/{value_lists[key]["file"]}', "r") as fd:
                data = json.load(fd)
                for feature in data:
                    del feature["json_featuretype"]
                    value_lists[key]["model"].objects.create(**feature)

            print(f"🤖 Values added for list {key}!")
