from django.core.management.base import BaseCommand
from django.db import transaction

from kablo.users.models import Group, User


class Command(BaseCommand):
    help = "Populate groups and demo users"

    @transaction.atomic
    def handle(self, *args, **options):
        editors, _ = Group.objects.get_or_create(name="editors")
        viewers, _ = Group.objects.get_or_create(name="viewers")

        viewer, _ = User.objects.get_or_create(username="demo_viewer")
        editor, _ = User.objects.get_or_create(username="demo_editor")
        super_user = User.objects.create_superuser(username="admin", is_staff=True)

        for user in (viewer, editor, super_user):
            user.set_password("123")
            user.save()

        editor.groups.add(editors)
        viewer.groups.add(viewers)

        editors.save()
        viewers.save()

        print(
            f"👥 added users 'demo_editor' & 'demo_viewer' to group 'editors' and 'viewers' respectively."
        )
