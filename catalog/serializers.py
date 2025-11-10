from rest_framework import serializers
from django.conf import settings
from .models import Category, Product, ProductImage


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


class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "description", "image", "is_active")

    def get_image(self, obj):
        return obj.image if obj.image else None
