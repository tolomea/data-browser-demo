import random

import faker_microservice
from data_browser.models import View
from django.contrib.auth.models import Group, Permission
from django.utils import timezone
from faker import Faker

from core import models


def get_price():
    return random.random() * 123 + 1


def rand(probability):
    return random.random() < probability


def get_or_create_admin_user(username):
    fake = Faker()

    return models.User.objects.get_or_create(
        username=username,
        defaults=dict(
            email="example@example.org",
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            is_staff=True,
            is_active=True,
        ),
    )


def create_perm_group():
    all_core_view_perms = Permission.objects.filter(
        codename__startswith="view_", content_type__app_label="core"
    )
    make_public_perm = Permission.objects.get(codename="make_view_public")
    group = Group.objects.create()
    group.permissions.set(list(all_core_view_perms) + [make_public_perm])


def create_views(user):
    View.objects.create(
        owner=user,
        name="All Products",
        description="All Products currently on sale with prices and sellers, ordered by price.",
        model_name="core.Product",
        fields="id,name,price-0,user__first_name,user__last_name,user__email",
        query="onsale__equals=true",
        public=True,
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
        public=True,
    )
    View.objects.create(
        owner=user,
        name="Order statistics",
        description="Order count and total value pivoted by year and month.",
        model_name="core.OrderItem",
        fields="&order__submitted_time__year+0,order__submitted_time__month+1,total__sum,order__id__count",
        query="",
        public=True,
    )


def create_users_and_products(num_users, prob_user_has_product, prob_product_onsale):
    fake = Faker()
    fake.add_provider(faker_microservice.Provider)

    users = []
    products = []
    for i in range(num_users):
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

        while rand(prob_user_has_product):
            products.append(
                models.Product.objects.create(
                    user=user,
                    name=fake.microservice(),
                    price=get_price(),
                    onsale=rand(prob_product_onsale),
                )
            )
    return users, products


def create_orders(users, products, prob_user_has_order, prob_order_has_extra_items):
    fake = Faker()

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
        while rand(prob_user_has_order):
            submitted_time = timezone.make_aware(fake.date_time_between("-3y"))
            order = models.Order.objects.create(
                buyer=user, submitted_time=submitted_time
            )
            user.last_order = order
            user.save()
            make_order_item()
            while rand(prob_order_has_extra_items):
                make_order_item()
