from django.core.management.base import BaseCommand
from catalog.models import Category, Product, ProductImage


class Command(BaseCommand):
    help = "Clear the sample seed data created by seed_data.py (safe: only removes known SKUs/categories)."

    def handle(self, *args, **options):
        self.stdout.write("Clearing seeded products and categories (if present)...")

        skus = [
            "CH-001",
            "CH-002",
            "CH-003",
            "CH-004",
            "TB-001",
            "TB-002",
        ]

        names = [
            "Office Chairs",
            "Office Tables",
            "Workstations",
            "Meeting Tables",
            "Reception Desks",
            "Bookshelves",
            "Coffee Tables",
            "Storage Units",
        ]

        # Delete product images first
        images_deleted = 0
        for sku in skus:
            try:
                prod = Product.objects.filter(sku=sku).first()
                if prod:
                    images_deleted += ProductImage.objects.filter(product=prod).delete()[0]
            except Exception:
                continue

        prods_deleted = Product.objects.filter(sku__in=skus).delete()[0]
        cats_deleted = Category.objects.filter(name__in=names).delete()[0]

        self.stdout.write(self.style.SUCCESS(f"Deleted {prods_deleted} products, {cats_deleted} categories, and {images_deleted} images (if existed)."))
