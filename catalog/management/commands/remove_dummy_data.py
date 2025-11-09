from django.core.management.base import BaseCommand
from catalog.models import Category, Product, ProductImage


class Command(BaseCommand):
    help = "Detect and remove likely dummy/seed data (images from unsplash/pexels, seed SKUs, BADGE markers)."

    def add_arguments(self, parser):
        parser.add_argument("--yes", action="store_true", help="Delete without prompting")

    def handle(self, *args, **options):
        yes = options.get("yes", False)

        seed_category_names = [
            "Office Chairs",
            "Office Tables",
            "Workstations",
            "Meeting Tables",
            "Reception Desks",
            "Bookshelves",
            "Coffee Tables",
            "Storage Units",
        ]

        seed_sku_prefixes = ("CH-", "TB-")
        image_indicators = ("unsplash.com", "pexels.com", "images.unsplash.com")

        # Find categories
        cats = Category.objects.filter(name__in=seed_category_names)

        # Collect candidate product IDs from a few heuristics
        candidate_ids = set()

        # Products by SKU prefixes
        for prefix in seed_sku_prefixes:
            candidate_ids.update(Product.objects.filter(sku__startswith=prefix).values_list("pk", flat=True))

        # Products by image source
        for term in image_indicators:
            candidate_ids.update(Product.objects.filter(image__icontains=term).values_list("pk", flat=True))

        # Products with BADGE marker in description
        candidate_ids.update(Product.objects.filter(description__icontains="BADGE:").values_list("pk", flat=True))

        # Products that belong to seeded categories
        if cats.exists():
            candidate_ids.update(Product.objects.filter(category__in=cats).values_list("pk", flat=True))

        prod_candidates = Product.objects.filter(pk__in=list(candidate_ids))

        self.stdout.write(f"Found {prod_candidates.count()} product(s) that look like seed/dummy data.")
        for p in prod_candidates:
            self.stdout.write(f" - {p.pk}: {p.name} (sku={p.sku}) image={p.image}")

        self.stdout.write(f"Found {cats.count()} seed category(ies): {[c.name for c in cats]}")
        if not prod_candidates.exists() and not cats.exists():
            self.stdout.write(self.style.SUCCESS("No obvious dummy data found. Exiting."))
            return

        if not yes:
            confirm = input("Delete the above products and categories? Type 'yes' to confirm: ")
            if confirm.strip().lower() != "yes":
                self.stdout.write(self.style.WARNING("Aborted by user."))
                return

        # Delete product images for these products first
        total_images_deleted = 0
        for p in prod_candidates:
            imgs_deleted = ProductImage.objects.filter(product=p).delete()[0]
            total_images_deleted += imgs_deleted

        prods_deleted = prod_candidates.delete()[0]
        cats_deleted = cats.delete()[0]

        self.stdout.write(self.style.SUCCESS(f"Deleted {prods_deleted} products, {cats_deleted} categories and {total_images_deleted} images."))
