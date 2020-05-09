from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    last_order = models.ForeignKey(
        "Order", on_delete=models.CASCADE, null=True, blank=True, related_name="+"
    )


class Product(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, blank=False, related_name="products"
    )
    name = models.CharField(blank=False, max_length=32)
    price = models.DecimalField(blank=False, decimal_places=2, max_digits=10)
    onsale = models.BooleanField()


class Order(models.Model):
    submitted_time = models.DateTimeField()
    buyer = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, blank=False, related_name="orders"
    )

    @property
    def total(self):
        return sum(item.total for item in self.order_items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="order_items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="order_items",
    )
    price = models.DecimalField(blank=False, decimal_places=2, max_digits=10)
    quantity = models.IntegerField(blank=False)

    @property
    def total(self):
        return self.price * self.quantity
