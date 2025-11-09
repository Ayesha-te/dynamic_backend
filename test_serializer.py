import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from catalog.models import Product
from catalog.serializers import ProductSerializer

products = Product.objects.all()[:1]
if products:
    product = products[0]
    print(f"Product: {product.name}")
    print(f"Category: {product.category}")
    print(f"Category type: {type(product.category)}")
    serializer = ProductSerializer(product)
    print("Serialized data:")
    print(json.dumps(serializer.data, indent=2, default=str))
else:
    print("No products found")
