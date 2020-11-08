from django.core.management.base import BaseCommand

from core import fixtures


class Command(BaseCommand):
    help = "Create demo site data"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("creating users and products"))
        all_users, all_products = fixtures.create_users_and_products(
            num_users=50, prob_user_has_product=0.5, prob_product_onsale=0.9
        )

        self.stdout.write(self.style.SUCCESS("creating orders"))
        for user in all_users:
            if fixtures.rand(0.99):
                products = [p for p in all_products if p.user.country == user.country]
            else:
                products = all_products

            fixtures.create_orders(
                user,
                products,
                prob_user_has_order=0.75,
                prob_order_has_extra_items=0.5,
            )

        user1 = all_users[0]
        user2 = all_users[1]
        assert user1.country != user2.country
        products = user2.products.all()
        fixtures.create_orders(user1, products, 0.8, 0.8)
