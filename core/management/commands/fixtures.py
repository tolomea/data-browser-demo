from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission
from core import models
from data_browser.models import View
from django.contrib.contenttypes.models import ContentType
from faker import Faker
import faker_microservice
import random
from django.utils import timezone

PRODUCT_ONSALE = 0.9
USER_HAS_PRODUCT = 0.5
USER_HAS_ORDER = 0.75
ORDER_HAS_EXTRA_ITEMS = 0.5


def price():
    return random.random() * 123 + 1


def rand(probability):
    return random.random() < probability


class Command(BaseCommand):
    help = "Create demo site data"

    def handle(self, *args, **options):
        fake = Faker()
        fake.add_provider(faker_microservice.Provider)

        self.stdout.write(self.style.SUCCESS("creating admin user"))
        admin = models.User.objects.create(
            email="admin@example.org",
            username="admin",
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            is_staff=True,
            is_active=True,
        )

        self.stdout.write(self.style.SUCCESS("adding permissions"))
        all_can_view_perms = Permission.objects.filter(codename__startswith="view_")
        view_content_type = ContentType.objects.get_for_model(View)
        all_ddb_view_perms = Permission.objects.filter(content_type=view_content_type)
        admin.user_permissions.set(list(all_can_view_perms) + list(all_ddb_view_perms))

        self.stdout.write(self.style.SUCCESS("creating users and products"))
        users = []
        products = []
        for i in range(100):
            first_name = fake.first_name()
            user = models.User.objects.create(
                email=fake.email(),
                username=f"{first_name}{i:02}",
                first_name=first_name,
                last_name=fake.last_name(),
                is_staff=False,
                is_active=True,
            )
            users.append(user)

            while rand(USER_HAS_PRODUCT):
                products.append(
                    models.Product.objects.create(
                        user=user,
                        name=fake.microservice(),
                        price=price(),
                        onsale=rand(PRODUCT_ONSALE),
                    )
                )

        self.stdout.write(self.style.SUCCESS("creating orders"))

        def make_order_item():
            product = random.choice(products)
            models.OrderItem.objects.create(
                order=order,
                product=product,
                price=price() if rand(0.1) else product.price,
                quantity=random.randrange(1, 20),
            )

        for user in users:
            while rand(USER_HAS_ORDER):
                submitted_time = timezone.make_aware(fake.date_time_this_decade())
                order = models.Order.objects.create(
                    buyer=user, submitted_time=submitted_time
                )
                user.last_order = order
                user.save()
                make_order_item()
                while rand(ORDER_HAS_EXTRA_ITEMS):
                    make_order_item()
