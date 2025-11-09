import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.test import APIClient
from io import BytesIO
from PIL import Image

from catalog.models import Product

client = APIClient()

# Get or create a test admin user
admin_user, _ = User.objects.get_or_create(
    username='testadmin',
    defaults={'is_staff': True, 'is_superuser': True}
)
admin_user.set_password('testpass123')
admin_user.save()

# Get the product
product = Product.objects.first()
if not product:
    print("No product found")
    exit(1)

print(f"Testing upload for product: {product.id} - {product.name}")

# Create a test image
img = Image.new('RGB', (100, 100), color='red')
img_io = BytesIO()
img.save(img_io, format='JPEG')
img_io.seek(0)

# Force authenticate
client.force_authenticate(user=admin_user)

# Try to upload
url = f'/api/catalog/admin/products/{product.id}/upload-image/'
print(f"Uploading to: {url}")

response = client.post(
    url,
    {
        'image': img_io,
        'color': 'Red',
        'alt_text': 'Test image'
    },
    format='multipart'
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.data if hasattr(response, 'data') else response.content}")
