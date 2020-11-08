from collections import defaultdict

from django.core.management.base import BaseCommand

from core import fixtures


class Command(BaseCommand):
    help = "Create demo site data"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("creating users and products"))
        all_users, all_products = fixtures.create_users_and_products(
            num_users=200, prob_user_has_product=0.5, prob_product_onsale=0.9
        )
        products_by_country = defaultdict(list)
        for product in all_products:
            products_by_country[product.user.country].append(product)

        self.stdout.write(self.style.SUCCESS("creating orders"))
        for user in all_users:
            if fixtures.rand(0.95):
                products = products_by_country[user.country]
            else:
                products = all_products

            fixtures.create_orders(
                user,
                products,
                prob_user_has_order=0.75,
                prob_order_has_extra_items=0.5,
            )

        user1 = all_users[0]
        for co in products_by_country:
            if co != user1.country:
                products = products_by_country[co][0].user.products.all()
                break
        else:
            assert False
        fixtures.create_orders(user1, products, 0.75, 0.5, 20)
