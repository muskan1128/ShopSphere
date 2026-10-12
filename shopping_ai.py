from models import Product
import re


def shopping_assistant(message):

    message = message.lower()

    products = Product.query.all()

    # =========================
    # BUDGET DETECTION
    # =========================

    budget = None

    budget_patterns = [
        r"under\s*(\d+)",
        r"below\s*(\d+)",
        r"less than\s*(\d+)",
        r"within\s*(\d+)",
        r"upto\s*(\d+)",
        r"up to\s*(\d+)",
        r"budget\s*(?:is|of)?\s*(\d+)",
        r"(\d+)\s*(?:rs|pkr|rupees)"
    ]

    for pattern in budget_patterns:

        match = re.search(pattern, message)

        if match:
            budget = float(match.group(1))
            break

    # =========================
    # CATEGORY DETECTION
    # =========================

    category_keywords = {
        "electronics": "electronics",
        "electronic": "electronics",
        "fashion": "fashion",
        "clothes": "fashion",
        "clothing": "fashion",
        "accessories": "accessories",
        "accessory": "accessories",
        "home": "home"
    }

    selected_category = None

    for keyword, category in category_keywords.items():

        if keyword in message:
            selected_category = category
            break

    # =========================
    # PRODUCT KEYWORDS
    # =========================

    product_keywords = {
        "headphone": "wireless headphones",
        "headphones": "wireless headphones",
        "headset": "wireless headphones",

        "watch": "smart watch",
        "smartwatch": "smart watch",

        "shoe": "running shoes",
        "shoes": "running shoes",
        "running": "running shoes",

        "backpack": "laptop backpack",
        "bag": "laptop backpack",

        "hoodie": "classic hoodie",
        "hood": "classic hoodie",

        "coffee": "coffee maker",
        "coffee maker": "coffee maker"
    }

    selected_product = None

    for keyword, product_name in product_keywords.items():

        if keyword in message:
            selected_product = product_name
            break

    # =========================
    # FIND PRODUCTS
    # =========================

    matches = []

    for product in products:

        product_name = product.name.lower()
        product_category = product.category.lower()

        # Exact product match
        if selected_product and selected_product in product_name:
            matches.append(product)
            continue

        # Category match
        if selected_category and product_category == selected_category:
            matches.append(product)
            continue

    # =========================
    # APPLY BUDGET
    # =========================

    if budget is not None:

        matches = [
            product
            for product in matches
            if product.price <= budget
        ]

    # =========================
    # ONLY BUDGET
    # =========================

    if not matches and budget is not None:

        matches = [
            product
            for product in products
            if product.price <= budget
        ]

    return matches[:5]


# =========================
# PRODUCT COMPARISON
# =========================

def compare_products(message):

    message = message.lower()

    products = Product.query.all()

    found_products = []

    for product in products:

        if product.name.lower() in message:
            found_products.append(product)

    return found_products[:2]