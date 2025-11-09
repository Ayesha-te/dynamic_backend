from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "slug", "is_active", "created_at")
	search_fields = ("name", "slug")


class ProductImageInline(admin.TabularInline):
	model = ProductImage
	fields = ("image", "color", "alt_text", "ordering", "image_preview")
	readonly_fields = ("image_preview",)
	extra = 1

	def image_preview(self, obj):
		if obj.image:
			return format_html('<img src="{}" width="75" height="75" />', obj.image.url)
		return "No image"
	image_preview.short_description = "Preview"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "sku", "price", "stock", "is_active", "image_preview")
	list_filter = ("is_active", "category")
	search_fields = ("name", "sku")
	readonly_fields = ("image_preview",)
	inlines = [ProductImageInline]

	def image_preview(self, obj):
		if obj.image:
			return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
		return "No image"
	image_preview.short_description = "Main Image"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
	list_display = ("id", "product", "color", "ordering", "image_preview")
	list_filter = ("product",)
	readonly_fields = ("image_preview",)

	def image_preview(self, obj):
		if obj.image:
			return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
		return "No image"
	image_preview.short_description = "Image Preview"
