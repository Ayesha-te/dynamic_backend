import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings

print('MEDIA_ROOT:', settings.MEDIA_ROOT)
print('MEDIA_URL:', settings.MEDIA_URL)
print('MEDIA_ROOT exists:', os.path.exists(settings.MEDIA_ROOT))
print('MEDIA_ROOT is writable:', os.access(settings.MEDIA_ROOT, os.W_OK))

img_dir = os.path.join(settings.MEDIA_ROOT, 'products', 'images')
print('\nImages dir:', img_dir)
print('Images dir exists:', os.path.exists(img_dir))

if os.path.exists(img_dir):
    files = os.listdir(img_dir)
    print(f'Files in images dir ({len(files)}):')
    for f in files[:10]:
        print(f'  - {f}')
