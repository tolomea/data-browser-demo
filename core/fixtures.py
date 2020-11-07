import random
from itertools import chain

import faker_microservice
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
            is_superuser=True,
        ),
    )


def create_users_and_products(num_users, prob_user_has_product, prob_product_onsale):
    fake = Faker()
    fake.add_provider(faker_microservice.Provider)
    country_choices = list(
        chain.from_iterable(
            [key] * len(value)
            for key, value in models.User._meta.get_field("country").choices
        )
    )

    users = []
    products = []
    for i in range(num_users):
        first_name = fake.first_name()
        country = random.choice(country_choices)
        user = models.User.objects.create(
            email=fake.email(),
            username=f"{first_name}{i:02}",
            first_name=first_name,
            last_name=fake.last_name(),
            country=country,
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
