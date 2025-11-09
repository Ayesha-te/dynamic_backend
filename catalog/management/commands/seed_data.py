from django.core.management.base import BaseCommand
from catalog.models import Category, Product, ProductImage


class Command(BaseCommand):
    help = "Seed the database with initial categories and products for development/testing."

    def handle(self, *args, **options):
        self.stdout.write("Seeding categories and products...")

        categories = [
            {"name": "Sofas & Couches", "description": "Comfortable seating for living rooms and lounges."},
            {"name": "Dining Furniture", "description": "Dining tables, chairs, and sets."},
            {"name": "Bedroom Furniture", "description": "Beds, wardrobes, and bedroom essentials."},
            {"name": "Office Furniture", "description": "Desks, chairs, and office solutions."},
            {"name": "Storage Solutions", "description": "Cabinets, shelves, and storage units."},
            {"name": "Coffee Tables", "description": "Modern and classic coffee tables."},
            {"name": "Outdoor Furniture", "description": "Garden and patio furniture."},
            {"name": "Accent Furniture", "description": "Side tables, benches, and decorative pieces."},
        ]

        created_categories = []
        for cat in categories:
            cobj, created = Category.objects.get_or_create(name=cat["name"], defaults={"description": cat["description"]})
            created_categories.append(cobj)

        products = [
            # Sofas & Couches
            {"name": "Modern Gray L-Shape Sofa", "price": "2500.00", "image": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800", "category": "Sofas & Couches", "sku": "SO-001", "stock": 5, "description": "Spacious L-shaped sofa in elegant gray fabric. Perfect for modern living rooms."},
            {"name": "Classic Leather Sectional", "price": "3200.00", "image": "https://images.unsplash.com/photo-1493857671505-72967e2e2760?w=800", "category": "Sofas & Couches", "sku": "SO-002", "stock": 3, "description": "Premium leather sectional with comfortable seating for the whole family."},
            {"name": "Contemporary Black Sofa", "price": "1800.00", "image": "https://images.unsplash.com/photo-1506439773649-6e0eb8cfb237?w=800", "category": "Sofas & Couches", "sku": "SO-003", "stock": 8, "description": "Sleek black sofa with modern design and quality construction."},
            
            # Dining Furniture
            {"name": "6-Seater Dining Table Set", "price": "2800.00", "image": "https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?w=800", "category": "Dining Furniture", "sku": "DT-001", "stock": 4, "description": "Complete dining set with table and 6 comfortable chairs."},
            {"name": "Glass Dining Table", "price": "1500.00", "image": "https://images.unsplash.com/photo-1493857671505-72967e2e2760?w=800", "category": "Dining Furniture", "sku": "DT-002", "stock": 6, "description": "Modern glass dining table perfect for contemporary kitchens."},
            {"name": "Wooden Dining Chairs (Set of 4)", "price": "800.00", "image": "https://images.unsplash.com/photo-1551632786-de41ec0dfce6?w=800", "category": "Dining Furniture", "sku": "DT-003", "stock": 10, "description": "Elegant wooden dining chairs with cushioned seats."},
            
            # Bedroom Furniture
            {"name": "Queen Size Bed Frame", "price": "1800.00", "image": "https://images.unsplash.com/photo-1540932239986-310128078ceb?w=800", "category": "Bedroom Furniture", "sku": "BD-001", "stock": 5, "description": "Sturdy queen-size bed frame with modern design."},
            {"name": "Wardrobe with Mirror", "price": "2200.00", "image": "https://images.unsplash.com/photo-1565693566231-b2a42eb4ab1d?w=800", "category": "Bedroom Furniture", "sku": "BD-002", "stock": 3, "description": "Spacious wardrobe with full-length mirror and multiple compartments."},
            {"name": "Nightstand with Drawer", "price": "400.00", "image": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800", "category": "Bedroom Furniture", "sku": "BD-003", "stock": 12, "description": "Compact nightstand with storage drawer for bedroom essentials."},
            
            # Office Furniture
            {"name": "Executive Desk", "price": "1600.00", "image": "https://images.unsplash.com/photo-1595526114035-0d45ed16cfbf?w=800", "category": "Office Furniture", "sku": "OF-001", "stock": 4, "description": "Professional executive desk with spacious work surface."},
            {"name": "Ergonomic Office Chair", "price": "900.00", "image": "https://images.unsplash.com/photo-1580480055273-228ff5388ef8?w=800", "category": "Office Furniture", "sku": "OF-002", "stock": 8, "description": "Adjustable ergonomic chair for long working hours."},
            {"name": "Bookshelf Unit", "price": "1200.00", "image": "https://images.unsplash.com/photo-1594878306623-48f60dde4eff?w=800", "category": "Office Furniture", "sku": "OF-003", "stock": 6, "description": "Tall bookshelf with multiple shelves for storage and display."},
            
            # Storage Solutions
            {"name": "Wall-Mounted Cabinet", "price": "700.00", "image": "https://images.unsplash.com/photo-1565693566231-b2a42eb4ab1d?w=800", "category": "Storage Solutions", "sku": "ST-001", "stock": 10, "description": "Modern wall-mounted cabinet for kitchen or bathroom."},
            {"name": "Under-Bed Storage Box", "price": "350.00", "image": "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=800", "category": "Storage Solutions", "sku": "ST-002", "stock": 15, "description": "Large storage box perfect for organizing under the bed."},
            
            # Coffee Tables
            {"name": "Wooden Coffee Table", "price": "650.00", "image": "https://images.unsplash.com/photo-1509936776144-2a96d64e3235?w=800", "category": "Coffee Tables", "sku": "CT-001", "stock": 7, "description": "Classic wooden coffee table with elegant design."},
            {"name": "Glass Top Coffee Table", "price": "550.00", "image": "https://images.unsplash.com/photo-1500644747242-a7d51da65a28?w=800", "category": "Coffee Tables", "sku": "CT-002", "stock": 9, "description": "Modern glass coffee table with stainless steel frame."},
            
            # Outdoor Furniture
            {"name": "Patio Dining Set", "price": "2000.00", "image": "https://images.unsplash.com/photo-1517457373614-b7152f800a81?w=800", "category": "Outdoor Furniture", "sku": "OT-001", "stock": 3, "description": "Weather-resistant patio dining set for outdoor entertaining."},
            {"name": "Garden Lounge Chair", "price": "450.00", "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800", "category": "Outdoor Furniture", "sku": "OT-002", "stock": 8, "description": "Comfortable lounge chair for garden relaxation."},
            
            # Accent Furniture
            {"name": "Console Table", "price": "500.00", "image": "https://images.unsplash.com/photo-1532372320572-cda25653213f?w=800", "category": "Accent Furniture", "sku": "AC-001", "stock": 6, "description": "Elegant console table for entryways and living rooms."},
            {"name": "Ottoman Bench", "price": "380.00", "image": "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=800", "category": "Accent Furniture", "sku": "AC-002", "stock": 9, "description": "Versatile ottoman bench for extra seating and storage."},
        ]

        for p in products:
            cat = Category.objects.get(name=p["category"])
            prod, created = Product.objects.get_or_create(sku=p["sku"], defaults={
                "category": cat,
                "name": p["name"],
                "price": p["price"],
                "image": p.get("image", ""),
                "stock": p.get("stock", 0),
                "description": p.get("description", ""),
                "is_active": True,
            })
            # add product image entry
            if p.get("image"):
                ProductImage.objects.get_or_create(product=prod, image_url=p["image"], defaults={"alt_text": prod.name})

        self.stdout.write(self.style.SUCCESS("Seeding complete."))
