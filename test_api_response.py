import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from catalog.models import Product
from catalog.serializers import ProductSerializer
from django.test import RequestFactory

factory = RequestFactory()
request = factory.get('/api/catalog/products/')

products = Product.objects.all()
print(f"Total products: {products.count()}\n")

for product in products[:1]:
    serializer = ProductSerializer(product, context={'request': request})
    data = serializer.data
    print(f"Product: {product.name}")
    print(f"Serialized data:\n{json.dumps(data, indent=2)}")
