from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, ProductDiscount


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "slug", "parent_category", "is_active", "created_at")
	list_filter = ("is_active", "parent_category")
	search_fields = ("name", "slug")
	fieldsets = (
		('Category Information', {
			'fields': ('name', 'slug', 'description', 'image', 'parent_category', 'is_active')
		}),
		('Metadata', {
			'fields': ('created_at', 'updated_at'),
			'classes': ('collapse',)
		}),
	)
	readonly_fields = ('created_at', 'updated_at')


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
	list_display = ("id", "name", "sku", "price", "delivery_charges", "stock", "is_active", "image_preview")
	list_filter = ("is_active", "category")
	search_fields = ("name", "sku")
	readonly_fields = ("image_preview",)
	inlines = [ProductImageInline,]


	def image_preview(self, obj):
		if obj.image:
			return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
		return "No image"
	image_preview.short_description = "Main Image"


class ProductDiscountInline(admin.StackedInline):
    model = ProductDiscount
    can_delete = True
    fields = ("original_price", "discount_price", "is_active")
    extra = 0



# Add discount inline to product edit so admin can create/edit/delete discount directly
ProductAdmin.inlines.append(ProductDiscountInline)


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


@admin.register(ProductDiscount)
class ProductDiscountAdmin(admin.ModelAdmin):
	list_display = ("id", "product", "original_price", "discount_price", "is_active", "created_at")
	list_filter = ("is_active", "created_at")
	search_fields = ("product__name", "product__sku")
	readonly_fields = ("created_at", "updated_at")
	fieldsets = (
		('Discount Information', {
			'fields': ('product', 'original_price', 'discount_price', 'is_active')
		}),
		('Metadata', {
			'fields': ('created_at', 'updated_at'),
			'classes': ('collapse',)
		}),
	)
