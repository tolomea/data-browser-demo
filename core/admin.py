from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AbstractUserAdmin
from django.db.models import F, FloatField, Sum
from django.db.models.functions import Cast

from . import models


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    fields = ["user", "name", "price", "onsale"]


class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    fields = ["product", "price", "quantity", "total"]
    readonly_fields = ["total"]
    extra = 0

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            total=Cast(F("price") * F("quantity"), output_field=FloatField())
        )

    def total(self, obj):
        return obj.total

    total.admin_order_field = "total"


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["submitted_time", "buyer", "total"]
    fields = ["submitted_time", "buyer", "total"]
    inlines = [OrderItemInline]
    readonly_fields = ["total"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            total=Sum(
                F("order_items__price") * F("order_items__quantity"),
                output_field=FloatField(),
            )
        )

    def total(self, obj):
        return obj.total

    total.admin_order_field = "total"


@admin.register(models.User)
class UserAdmin(AbstractUserAdmin):
    fieldsets = list(AbstractUserAdmin.fieldsets) + [
        (None, {"fields": ["last_order", "country"]})
    ]
