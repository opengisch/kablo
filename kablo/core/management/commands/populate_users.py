from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Populate db with demo user"

    @transaction.atomic
    def handle(self, *args, **options):
        user = get_user_model()
        user.objects.all().delete()

        # Create superuser
        user.objects.create_user(
            email=None,
            first_name="admin",
            last_name="admin",
            username="admin",
            password="admin",
            is_staff=True,
            is_superuser=True,
        )
