from rest_framework import serializers
from .models import Blog, BlogImage


class BlogImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = BlogImage
        fields = ("id", "image", "alt_text", "ordering")

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


class BlogSerializer(serializers.ModelSerializer):
    featured_image = serializers.ImageField(use_url=True, required=False, allow_null=True)
    pdf_file = serializers.FileField(use_url=True, required=False, allow_null=True)
    pdf_thumbnail = serializers.ImageField(use_url=True, required=False, allow_null=True)
    blog_type = serializers.CharField(required=False)
    images = BlogImageSerializer(many=True, read_only=True)

    class Meta:
        model = Blog
        fields = (
            'id',
            'title',
            'slug',
            'blog_type',
            'excerpt',
            'content',
            'featured_image',
            'pdf_file',
            'pdf_thumbnail',
            'is_published',
            'images',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at', 'slug')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        
        if ret.get('featured_image'):
            image_url = ret['featured_image']
            if image_url and not image_url.startswith('http'):
                if not image_url.startswith('/media/'):
                    image_url = f"/media/{image_url}"
                request = self.context.get('request')
                if request:
                    ret['featured_image'] = request.build_absolute_uri(image_url)
                else:
                    ret['featured_image'] = image_url
        
        if ret.get('pdf_file'):
            pdf_url = ret['pdf_file']
            if pdf_url and not pdf_url.startswith('http'):
                if not pdf_url.startswith('/media/'):
                    pdf_url = f"/media/{pdf_url}"
                request = self.context.get('request')
                if request:
                    ret['pdf_file'] = request.build_absolute_uri(pdf_url)
                else:
                    ret['pdf_file'] = pdf_url
        
        if ret.get('pdf_thumbnail'):
            thumb_url = ret['pdf_thumbnail']
            if thumb_url and not thumb_url.startswith('http'):
                if not thumb_url.startswith('/media/'):
                    thumb_url = f"/media/{thumb_url}"
                request = self.context.get('request')
                if request:
                    ret['pdf_thumbnail'] = request.build_absolute_uri(thumb_url)
                else:
                    ret['pdf_thumbnail'] = thumb_url
        
        return ret
