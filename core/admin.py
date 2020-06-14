from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AbstractUserAdmin
from . import models


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    fields = ["user", "name", "price", "onsale"]


class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    fields = ["product", "price", "quantity", "total"]


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    fields = ["submitted_time", "buyer"]
    inlines = [OrderItemInline]


@admin.register(models.User)
class UserAdmin(AbstractUserAdmin):
    fieldsets = list(AbstractUserAdmin.fieldsets) + [
        ("History", {"fields": ["last_order"]})
    ]
