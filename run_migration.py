import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.management import call_command

try:
    print("Running migrations for blogs app...")
    call_command('migrate', 'blogs', verbosity=2)
    print("Migration completed successfully!")
except Exception as e:
    print(f"Error during migration: {str(e)}")
    sys.exit(1)
