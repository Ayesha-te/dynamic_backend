from rest_framework import serializers
from .models import Newsletter
from django.db import IntegrityError


class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = ['id', 'email', 'subscribed_at', 'is_active']
        read_only_fields = ['id', 'subscribed_at']


class NewsletterSubscribeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    
    class Meta:
        model = Newsletter
        fields = ['email']
    
    def create(self, validated_data):
        try:
            newsletter, created = Newsletter.objects.get_or_create(
                email=validated_data['email'],
                defaults={'is_active': True}
            )
        except IntegrityError:
            # race condition: another request created the same email concurrently
            newsletter = Newsletter.objects.filter(email=validated_data['email']).first()
            if not newsletter:
                # propagate if something else went wrong
                raise

        if not newsletter.is_active:
            newsletter.is_active = True
            newsletter.save()
        return newsletter
