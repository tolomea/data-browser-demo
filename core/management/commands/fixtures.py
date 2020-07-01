from core import fixtures
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create demo site data"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("creating perm group"))
        fixtures.create_perm_group()

        self.stdout.write(self.style.SUCCESS("creating users and products"))
        users, products = fixtures.create_users_and_products(
            num_users=50, prob_user_has_product=0.5, prob_product_onsale=0.9
        )

        self.stdout.write(self.style.SUCCESS("creating orders"))
        fixtures.create_orders(
            users, products, prob_user_has_order=0.75, prob_order_has_extra_items=0.5
        )
