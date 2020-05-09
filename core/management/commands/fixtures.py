from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission
from core.models import User
from data_browser.models import View
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = "Create demo site data"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("creating user"))
        user = User.objects.create(
            email="admin@example.org",
            username="admin",
            first_name="Jon",
            last_name="Doe",
            is_staff=True,
            is_active=True,
        )

        self.stdout.write(self.style.SUCCESS("adding permissions"))
        all_can_view_perms = Permission.objects.filter(codename__startswith="view_")
        view_content_type = ContentType.objects.get_for_model(View)
        all_ddb_view_perms = Permission.objects.filter(content_type=view_content_type)
        user.user_permissions.set(list(all_can_view_perms) + list(all_ddb_view_perms))
