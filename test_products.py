import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from catalog.models import Product, ProductImage

print('=== Products ===')
products = Product.objects.all()
print(f'Total products: {products.count()}')
for p in products:
    print(f'  ID: {p.id}, Name: {p.name}, Has image: {bool(p.image)}, Image name: {p.image.name if p.image else "None"}')

print('\n=== ProductImages ===')
images = ProductImage.objects.all()
print(f'Total product images: {images.count()}')
for img in images[:5]:
    print(f'  ID: {img.id}, Product: {img.product.name}, Image: {img.image.name if img.image else "None"}')
