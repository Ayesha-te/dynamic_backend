import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from catalog.models import ProductImage, Product

print("=== Products ===")
products = Product.objects.all()
for p in products:
    print(f"ID: {p.id}, Name: {p.name}, Main Image: {p.image.name if p.image else 'EMPTY'}")

print("\n=== Recent ProductImages ===")
recent = ProductImage.objects.order_by('-id')[:10]
for img in recent:
    print(f"ID: {img.id}, Product: {img.product.name}, Image: {img.image.name if img.image else 'EMPTY'}, Color: {img.color}")
