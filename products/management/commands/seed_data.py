from django.core.management.base import BaseCommand
from products.models import Category, Product, ProductVariant


class Command(BaseCommand):
    help = 'Seed database with sample categories and products for MJ Ekdantay Masala Centre'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # Create categories
        categories_data = [
            {'name': 'Whole Spices', 'slug': 'whole-spices', 'description': 'Premium whole spices sourced directly from farms. Retain maximum flavour and aroma.'},
            {'name': 'Blended Masala', 'slug': 'blended-masala', 'description': 'Expertly blended masala powders ground fresh for authentic Indian cooking.'},
            {'name': 'Special Masala', 'slug': 'special-masala', 'description': 'Signature spice blends crafted with secret family recipes for extraordinary taste.'},
            {'name': 'Dry Fruits & Seeds', 'slug': 'dry-fruits-seeds', 'description': 'Premium quality dry fruits and seeds for cooking and snacking.'},
        ]

        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories[cat.name] = cat
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  {status}: Category "{cat.name}"')

        # Create products with variants
        products_data = [
            {
                'name': 'Haldi (Turmeric) Powder',
                'slug': 'haldi-turmeric-powder',
                'description': 'Pure turmeric powder with a vibrant golden colour. An essential spice for Indian cooking known for its earthy flavour and health benefits.',
                'ingredients': 'Pure Turmeric (Curcuma longa)',
                'usage_info': 'Add to curries, dals, rice dishes, and milk. Can also be used as a natural food colouring.',
                'category': 'Blended Masala',
                'base_price': 45,
                'is_featured': True,
                'variants': [
                    {'weight_label': '100g', 'price': 45, 'stock_quantity': 100},
                    {'weight_label': '250g', 'price': 99, 'stock_quantity': 75},
                    {'weight_label': '500g', 'price': 185, 'stock_quantity': 50},
                ],
            },
            {
                'name': 'Lal Mirch (Red Chilli) Powder',
                'slug': 'lal-mirch-red-chilli-powder',
                'description': 'Fiery red chilli powder made from premium Kashmiri and Guntur chillies. Adds vibrant colour and spicy heat to any dish.',
                'ingredients': 'Red Chilli (Capsicum annuum)',
                'usage_info': 'Add to curries, marinades, chutneys, and snacks for heat and colour.',
                'category': 'Blended Masala',
                'base_price': 50,
                'is_featured': True,
                'variants': [
                    {'weight_label': '100g', 'price': 50, 'stock_quantity': 100},
                    {'weight_label': '250g', 'price': 115, 'stock_quantity': 75},
                    {'weight_label': '500g', 'price': 210, 'stock_quantity': 50},
                ],
            },
            {
                'name': 'Jeera (Cumin) Seeds',
                'slug': 'jeera-cumin-seeds',
                'description': 'Aromatic whole cumin seeds with strong earthy flavour. Essential for tempering (tadka) and adds depth to curries.',
                'ingredients': 'Cumin Seeds (Cuminum cyminum)',
                'usage_info': 'Use for tempering in hot oil, grind for spice blends, or toast and sprinkle on raita and salads.',
                'category': 'Whole Spices',
                'base_price': 60,
                'is_featured': True,
                'variants': [
                    {'weight_label': '100g', 'price': 60, 'stock_quantity': 80},
                    {'weight_label': '250g', 'price': 140, 'stock_quantity': 60},
                    {'weight_label': '500g', 'price': 260, 'stock_quantity': 40},
                ],
            },
            {
                'name': 'Garam Masala',
                'slug': 'garam-masala',
                'description': 'A fragrant blend of cinnamon, cardamom, cloves, black pepper, and other warming spices. The crown jewel of Indian spice blends.',
                'ingredients': 'Cinnamon, Cardamom, Cloves, Black Pepper, Bay Leaf, Mace, Nutmeg',
                'usage_info': 'Sprinkle at the end of cooking for maximum aroma. Perfect for curries, biryanis, and gravies.',
                'category': 'Special Masala',
                'base_price': 55,
                'is_featured': True,
                'variants': [
                    {'weight_label': '50g', 'price': 55, 'stock_quantity': 90},
                    {'weight_label': '100g', 'price': 99, 'stock_quantity': 70},
                    {'weight_label': '250g', 'price': 230, 'stock_quantity': 45},
                ],
            },
            {
                'name': 'Dhaniya (Coriander) Powder',
                'slug': 'dhaniya-coriander-powder',
                'description': 'Freshly ground coriander powder with a mild, citrusy flavour. A staple in every Indian kitchen.',
                'ingredients': 'Coriander Seeds (Coriandrum sativum)',
                'usage_info': 'Add to curries, soups, and marinades. Can be mixed with other powders for blends.',
                'category': 'Blended Masala',
                'base_price': 40,
                'is_featured': True,
                'variants': [
                    {'weight_label': '100g', 'price': 40, 'stock_quantity': 100},
                    {'weight_label': '250g', 'price': 90, 'stock_quantity': 80},
                    {'weight_label': '500g', 'price': 165, 'stock_quantity': 55},
                ],
            },
            {
                'name': 'Kali Mirch (Black Pepper)',
                'slug': 'kali-mirch-black-pepper',
                'description': 'Whole black peppercorns known as the "King of Spices". Bold, pungent flavour that elevates any dish.',
                'ingredients': 'Black Pepper (Piper nigrum)',
                'usage_info': 'Crush fresh for seasoning, use whole in biryanis and stews, or grind for table pepper.',
                'category': 'Whole Spices',
                'base_price': 70,
                'is_featured': True,
                'variants': [
                    {'weight_label': '50g', 'price': 70, 'stock_quantity': 65},
                    {'weight_label': '100g', 'price': 130, 'stock_quantity': 50},
                    {'weight_label': '250g', 'price': 300, 'stock_quantity': 30},
                ],
            },
            {
                'name': 'Chai Masala',
                'slug': 'chai-masala',
                'description': 'A warming blend of spices to make the perfect cup of Indian masala chai. Aromatic, comforting, and invigorating.',
                'ingredients': 'Ginger, Cardamom, Cinnamon, Cloves, Black Pepper, Fennel',
                'usage_info': 'Add half a teaspoon while boiling tea leaves and milk. Adjust to taste.',
                'category': 'Special Masala',
                'base_price': 65,
                'is_featured': False,
                'variants': [
                    {'weight_label': '50g', 'price': 65, 'stock_quantity': 85},
                    {'weight_label': '100g', 'price': 120, 'stock_quantity': 60},
                ],
            },
            {
                'name': 'Sabzi Masala',
                'slug': 'sabzi-masala',
                'description': 'A specially crafted blend for vegetable dishes. Makes everyday sabzi taste restaurant-quality.',
                'ingredients': 'Coriander, Cumin, Red Chilli, Turmeric, Amchur, Fenugreek, Asafoetida',
                'usage_info': 'Add one tablespoon per serving while cooking vegetables. Mix in after adding tomatoes.',
                'category': 'Special Masala',
                'base_price': 85,
                'is_featured': False,
                'variants': [
                    {'weight_label': '100g', 'price': 85, 'stock_quantity': 70},
                    {'weight_label': '250g', 'price': 195, 'stock_quantity': 50},
                    {'weight_label': '500g', 'price': 360, 'stock_quantity': 30},
                ],
            },
        ]

        for prod_data in products_data:
            variants_data = prod_data.pop('variants')
            category_name = prod_data.pop('category')
            prod_data['category'] = categories[category_name]

            product, created = Product.objects.get_or_create(
                slug=prod_data['slug'],
                defaults=prod_data
            )
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  {status}: Product "{product.name}"')

            if created:
                for var_data in variants_data:
                    ProductVariant.objects.create(product=product, **var_data)
                    self.stdout.write(f'    + Variant: {var_data["weight_label"]} @ ₹{var_data["price"]}')

        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully!'))
        self.stdout.write(f'  Categories: {Category.objects.count()}')
        self.stdout.write(f'  Products: {Product.objects.count()}')
        self.stdout.write(f'  Variants: {ProductVariant.objects.count()}')
