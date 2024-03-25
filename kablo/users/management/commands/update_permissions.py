from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Populate db with demo user"

    @transaction.atomic
    def handle(self, *args, **options):
        viewing = []
        editing = []

        models = []

        for _app in ("network", "editing"):
            for ct in ContentType.objects.filter(app_label=_app):
                m = ct.model_class()
                models.append(f"{m.__module__}.{m.__name__}")

                viewing.append(
                    Permission.objects.get(content_type=ct, codename__startswith="view")
                )

                editing.append(
                    Permission.objects.get(content_type=ct, codename__startswith="add")
                )
                editing.append(
                    Permission.objects.get(
                        content_type=ct, codename__startswith="change"
                    )
                )
                editing.append(
                    Permission.objects.get(
                        content_type=ct, codename__startswith="delete"
                    )
                )

        editing += viewing

        editors, _ = Group.objects.get_or_create(name="editors")
        viewers, _ = Group.objects.get_or_create(name="viewers")

        editors.permissions.set(editing)
        viewers.permissions.set(viewing)

        editors.save()
        viewers.save()

        print(f"👥 Permissions updated for {', '.join(models)}.")
