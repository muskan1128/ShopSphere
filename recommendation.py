from models import Product


def get_recommendations(product_id, limit=3):

    current_product = Product.query.get(product_id)

    if not current_product:
        return []

    # First priority: same category
    recommendations = Product.query.filter(
        Product.category == current_product.category,
        Product.id != current_product.id
    ).limit(limit).all()

    # If not enough products, add products from other categories
    if len(recommendations) < limit:

        extra_products = Product.query.filter(
            Product.id != current_product.id,
            Product.category != current_product.category
        ).limit(limit - len(recommendations)).all()

        recommendations.extend(extra_products)

    return recommendations