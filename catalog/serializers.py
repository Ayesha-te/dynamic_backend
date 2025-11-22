from rest_framework import serializers
from django.conf import settings
from .models import Category, Product, ProductImage, ProductDiscount
from decimal import Decimal


class ProductDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDiscount
        fields = ("id", "original_price", "discount_price", "is_active", "created_at")
        read_only_fields = ("created_at",)


class ProductImageSerializer(serializers.ModelSerializer):
    # Ensure serializer returns a URL for the image field (use_url=True)
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = ProductImage
        fields = ("id", "image", "color", "alt_text", "ordering")

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret.get('image'):
            image_url = ret['image']
            if image_url and not image_url.startswith('http'):
                if not image_url.startswith('/media/'):
                    image_url = f"/media/{image_url}"
                request = self.context.get('request')
                if request:
                    ret['image'] = request.build_absolute_uri(image_url)
                else:
                    ret['image'] = image_url
            return ret
        return ret


class ProductSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True, required=False, allow_null=True)
    images = ProductImageSerializer(many=True, read_only=True)
    category = serializers.SerializerMethodField(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False)
    discount = ProductDiscountSerializer(read_only=True)
    # Allow admin clients to set a discount price when creating/updating via admin endpoints
    discount_price = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True, required=False, allow_null=True)
    original_price = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True, required=False, allow_null=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "price",
            "delivery_charges",
            "sku",
            "image",
            "stock",
            "is_active",
            "category",
            "category_id",
            "images",
            "discount",
            "discount_price",
            "original_price",
        )
    
    def get_category(self, obj):
        if obj.category:
            return {
                "id": obj.category.id,
                "name": obj.category.name,
                "slug": obj.category.slug,
            }
        return None

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret.get('image'):
            image_url = ret['image']
            if image_url and not image_url.startswith('http'):
                if not image_url.startswith('/media/'):
                    image_url = f"/media/{image_url}"
                request = self.context.get('request')
                if request:
                    ret['image'] = request.build_absolute_uri(image_url)
                else:
                    ret['image'] = image_url
        return ret

    def to_representation(self, instance):
        # Use base representation then expose a top-level `discount_price` for convenience
        ret = super().to_representation(instance)
        # ensure image URL is absolute when possible (same logic as ProductImageSerializer)
        if ret.get('image'):
            image_url = ret['image']
            if image_url and not image_url.startswith('http'):
                if not image_url.startswith('/media/'):
                    image_url = f"/media/{image_url}"
                request = self.context.get('request')
                if request:
                    ret['image'] = request.build_absolute_uri(image_url)
                else:
                    ret['image'] = image_url

        try:
            if hasattr(instance, 'discount') and instance.discount:
                # expose numeric/string value at top level for frontend convenience
                ret['discount_price'] = str(instance.discount.discount_price)
                ret['original_price'] = str(instance.discount.original_price)
            else:
                # ensure keys exist (null when no discount)
                ret.setdefault('discount_price', None)
                ret.setdefault('original_price', None)
        except Exception:
            ret.setdefault('discount_price', None)
            ret.setdefault('original_price', None)
        return ret

    def validate_sku(self, value):
        request = self.context.get('request')
        if self.instance:
            if Product.objects.exclude(pk=self.instance.pk).filter(sku=value).exists():
                raise serializers.ValidationError("A product with this SKU already exists.")
        else:
            if Product.objects.filter(sku=value).exists():
                raise serializers.ValidationError("A product with this SKU already exists.")
        return value

    def validate(self, attrs):
        try:
            attrs = super().validate(attrs)
            
            if not self.instance and 'category_id' not in attrs:
                raise serializers.ValidationError({"category_id": "Category is required when creating a product."})
            
            if self.instance:
                name = attrs.get('name', self.instance.name)
            else:
                name = attrs.get('name')
            
            if name:
                from django.utils.text import slugify
                slug = slugify(name)
                if self.instance:
                    if Product.objects.exclude(pk=self.instance.pk).filter(slug=slug).exists():
                        raise serializers.ValidationError({"name": "A product with a similar name (slug) already exists."})
                else:
                    if Product.objects.filter(slug=slug).exists():
                        raise serializers.ValidationError({"name": "A product with a similar name (slug) already exists."})
            
            return attrs
        except serializers.ValidationError:
            raise
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception(f"Unexpected error during validation: {str(e)}")
            raise serializers.ValidationError(f"An error occurred during validation: {str(e)}")

    def create(self, validated_data):
        # Pop discount-related fields so they are not passed to Product.objects.create()
        discount_price = validated_data.pop('discount_price', None)
        original_price = validated_data.pop('original_price', None)

        # Handle category_id if provided (ModelSerializer will handle assignment normally)
        product = super().create(validated_data)

        # Create/update ProductDiscount if discount_price provided
        try:
            if discount_price not in (None, '', 'null'):
                dp = Decimal(str(discount_price))
                op = Decimal(str(original_price)) if original_price not in (None, '', 'null') else product.price
                ProductDiscount.objects.update_or_create(
                    product=product,
                    defaults={
                        'original_price': op,
                        'discount_price': dp,
                        'is_active': True,
                    }
                )
        except Exception:
            # Don't let discount creation break product creation; log and continue
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("Failed to create/update ProductDiscount in serializer.create")

        return product

    def update(self, instance, validated_data):
        # Pop discount fields so they are not treated as Product model fields
        discount_price = validated_data.pop('discount_price', None)
        original_price = validated_data.pop('original_price', None)

        product = super().update(instance, validated_data)

        # Manage discount creation/update/deletion based on incoming data
        try:
            if discount_price not in (None, '', 'null'):
                dp = Decimal(str(discount_price))
                op = Decimal(str(original_price)) if original_price not in (None, '', 'null') else product.price
                ProductDiscount.objects.update_or_create(
                    product=product,
                    defaults={
                        'original_price': op,
                        'discount_price': dp,
                        'is_active': True,
                    }
                )
            else:
                # If discount_price explicitly empty/null, remove existing discount
                if discount_price in (None, '', 'null'):
                    ProductDiscount.objects.filter(product=product).delete()
        except Exception:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("Failed to create/update/delete ProductDiscount in serializer.update")

        return product


class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    subcategories = serializers.SerializerMethodField()
    parent_category_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "description", "image", "is_active", "parent_category_id", "subcategories")

    def get_image(self, obj):
        return obj.image if obj.image else None
    
    def get_subcategories(self, obj):
        subcats = obj.subcategories.filter(is_active=True)
        return CategorySubcategorySerializer(subcats, many=True).data
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['parent_category_id'] = instance.parent_category_id if instance.parent_category_id else None
        return ret
    
    def create(self, validated_data):
        parent_category_id = validated_data.pop('parent_category_id', None)
        category = Category.objects.create(**validated_data)
        if parent_category_id:
            category.parent_category_id = parent_category_id
            category.save()
        return category
    
    def update(self, instance, validated_data):
        parent_category_id = validated_data.pop('parent_category_id', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if parent_category_id is not None:
            instance.parent_category_id = parent_category_id
        instance.save()
        return instance


class CategorySubcategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "description", "image", "is_active")

    def get_image(self, obj):
        return obj.image if obj.image else None
