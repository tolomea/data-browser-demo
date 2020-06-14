import random

import faker_microservice
from core import models
from data_browser.models import View
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

NUM_USERS = 50
PRODUCT_ONSALE = 0.9
USER_HAS_PRODUCT = 0.5
USER_HAS_ORDER = 0.75
ORDER_HAS_EXTRA_ITEMS = 0.5


def get_price():
    return random.random() * 123 + 1


def rand(probability):
    return random.random() < probability


class Command(BaseCommand):
    help = "Create demo site data"

    def create_admin_user(self):
        self.stdout.write(self.style.SUCCESS("creating admin user"))
        admin = models.User.objects.create(
            email="admin@example.org",
            username="admin",
            first_name=self.fake.first_name(),
            last_name=self.fake.last_name(),
            is_staff=True,
            is_active=True,
        )

        self.stdout.write(self.style.SUCCESS("adding permissions"))
        all_can_view_perms = Permission.objects.filter(codename__startswith="view_")
        view_content_type = ContentType.objects.get_for_model(View)
        all_ddb_view_perms = Permission.objects.filter(content_type=view_content_type)
        admin.user_permissions.set(list(all_can_view_perms) + list(all_ddb_view_perms))
        return admin

    def create_views(self, user):
        View.objects.create(
            owner=user,
            name="All Products",
            description="All Products currently on sale with prices and sellers, ordered by price.",
            model_name="core.Product",
            fields="id,name,price-0,user__first_name,user__last_name,user__email",
            query="onsale__equals=true",
        )
        View.objects.create(
            owner=user,
            name="People who brought databases",
            description=(
                "Everyone who brought some kind of database and what kind it was. "
                "Along with how many they brought and the total cost. "
                "We're using random data so it's possible there aren't any."
            ),
            model_name="core.OrderItem",
            fields="product__name,product__user__first_name,product__user__last_name,quantity__sum,price__sum-0",
            query="product__name__contains=database",
        )
        View.objects.create(
            owner=user,
            name="Order statistics",
            description="Order count and total value pivoted by year and month.",
            model_name="core.OrderItem",
            fields="&order__submitted_time__year+0,order__submitted_time__month+1,total__sum,order__id__count",
            query="",
        )

    def create_users_and_products(self):
        self.stdout.write(self.style.SUCCESS("creating users and products"))
        users = []
        products = []
        for i in range(NUM_USERS):
            first_name = self.fake.first_name()
            user = models.User.objects.create(
                email=self.fake.email(),
                username=f"{first_name}{i:02}",
                first_name=first_name,
                last_name=self.fake.last_name(),
                is_staff=False,
                is_active=True,
            )
            users.append(user)

            while rand(USER_HAS_PRODUCT):
                products.append(
                    models.Product.objects.create(
                        user=user,
                        name=self.fake.microservice(),
                        price=get_price(),
                        onsale=rand(PRODUCT_ONSALE),
                    )
                )
        return users, products

    def create_orders(self, users, products):
        self.stdout.write(self.style.SUCCESS("creating orders"))

        def make_order_item():
            product = random.choice(products)
            price = get_price() if rand(0.1) else product.price
            quantity = random.randrange(1, 20)
            models.OrderItem.objects.create(
                order=order,
                product=product,
                price=price,
                quantity=quantity,
                total=price * quantity,
            )

        for user in users:
            while rand(USER_HAS_ORDER):
                submitted_time = timezone.make_aware(self.fake.date_time_between("-3y"))
                order = models.Order.objects.create(
                    buyer=user, submitted_time=submitted_time
                )
                user.last_order = order
                user.save()
                make_order_item()
                while rand(ORDER_HAS_EXTRA_ITEMS):
                    make_order_item()

    def handle(self, *args, **options):
        self.fake = Faker()
        self.fake.add_provider(faker_microservice.Provider)

        admin = self.create_admin_user()
        self.create_views(admin)
        users, products = self.create_users_and_products()
        self.create_orders(users, products)
