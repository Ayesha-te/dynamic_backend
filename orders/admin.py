from django.contrib import admin

# Register your models here.
from .models import Cart, CartItem, Order, OrderItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "is_active", "created_at")
	list_filter = ("is_active",)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
	list_display = ("id", "cart", "product", "quantity")
	search_fields = ("product__name",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "status", "is_paid", "total_amount", "created_at")
	list_filter = ("status", "is_paid")
	readonly_fields = ("created_at", "updated_at", "paid_at")
	inlines = []
	actions = ["mark_as_paid", "mark_as_unpaid"]

	def mark_as_paid(self, request, queryset):
		from django.utils import timezone
		updated = queryset.update(is_paid=True, paid_at=timezone.now())
		self.message_user(request, f"Marked {updated} order(s) as paid.")

	mark_as_paid.short_description = "Mark selected orders as paid"

	def mark_as_unpaid(self, request, queryset):
		updated = queryset.update(is_paid=False, paid_at=None)
		self.message_user(request, f"Marked {updated} order(s) as unpaid.")

	mark_as_unpaid.short_description = "Mark selected orders as unpaid"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
	list_display = ("id", "order", "product", "quantity", "price")


# Attach inline OrderItems to OrderAdmin for easier editing
class OrderItemInline(admin.TabularInline):
	model = OrderItem
	extra = 0

OrderAdmin.inlines = [OrderItemInline]
