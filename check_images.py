import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from catalog.models import Product, ProductImage

products = Product.objects.all()
print(f"Total products: {products.count()}")

for p in products[:3]:
    print(f"\nProduct: {p.name}")
    print(f"  Main image field: {p.image}")
    print(f"  Related ProductImages: {p.images.all().count()}")
    for img in p.images.all():
        print(f"    - Color: {img.color}, Image: {img.image.name if img.image else 'EMPTY'}")
