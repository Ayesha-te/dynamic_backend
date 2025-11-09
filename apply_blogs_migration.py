#!/usr/bin/env python
import os
import sys
import django

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()
    
    from django.core.management import call_command
    
    print("Applying blogs migration...")
    try:
        call_command('migrate', 'blogs', verbosity=2)
        print("\n✓ Migration applied successfully!")
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        sys.exit(1)
