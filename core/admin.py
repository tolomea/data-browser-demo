from data_browser.helpers import AdminMixin, annotation
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AbstractUserAdmin
from django.db.models import F, FloatField, Sum
from django.db.models.functions import Cast

from . import models


@admin.register(models.Product)
class ProductAdmin(AdminMixin, admin.ModelAdmin):
    fields = ["user", "name", "price", "onsale"]


class OrderItemInline(AdminMixin, admin.TabularInline):
    model = models.OrderItem
    fields = ["product", "price", "quantity", "total"]
    extra = 0

    @annotation
    def total(self, request, qs):
        return qs.annotate(
            total=Cast(F("price") * F("quantity"), output_field=FloatField())
        )


@admin.register(models.Order)
class OrderAdmin(AdminMixin, admin.ModelAdmin):
    fields = ["submitted_time", "buyer", "total"]
    inlines = [OrderItemInline]

    @annotation
    def total(self, request, qs):
        return qs.annotate(
            total=Sum(
                F("order_items__price") * F("order_items__quantity"),
                output_field=FloatField(),
            )
        )


@admin.register(models.User)
class UserAdmin(AdminMixin, AbstractUserAdmin):
    fieldsets = list(AbstractUserAdmin.fieldsets) + [
        ("History", {"fields": ["last_order"]})
    ]
