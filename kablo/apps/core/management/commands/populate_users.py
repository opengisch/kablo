import sys

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from .functions import *


class Command(BaseCommand):
    help = "Populate db with demo user"

    @transaction.atomic
    def handle(self, *args, **options):
        """Populate db with testdata"""

        confirm_reset_data(sys)

        User = get_user_model()
        User.objects.all().delete()

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
