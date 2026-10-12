from flask import Flask, render_template, session, redirect, url_for, request, flash
from models import db, Product, Order, User
from recommendation import get_recommendations
from shopping_ai import shopping_assistant, compare_products
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)


app.secret_key = "shopsphere-secret-key"

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///shopsphere.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db.init_app(app)
@app.context_processor
def cart_count():
    cart = session.get("cart", {})
    count = sum(cart.values())

    return {
        "cart_count": count
    }

# =========================
# HOME
# =========================

@app.route("/")
def home():
    return render_template("index.html")


# =========================
# REGISTER
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            flash("Username or email already exists!", "error")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        user = User(
            username=username,
            email=email,
            password=hashed_password,
            role="customer"
        )

        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role

            flash("Login successful! 🎉", "success")

            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))

            return redirect(url_for("home"))

        flash("Invalid email or password!", "error")

    return render_template("login.html")


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.pop("user_id", None)
    session.pop("username", None)
    session.pop("role", None)

    flash("You have been logged out.", "success")

    return redirect(url_for("home"))


# =========================
# SHOP
# =========================

@app.route("/shop")
def shop():
    products = Product.query.all()
    print("PRODUCTS:", products)

    return render_template(
        "shop.html",
        products=products
    )


# =========================
# PRODUCT DETAILS
# =========================

@app.route("/product/<int:product_id>")
def product_detail(product_id):

    product = Product.query.get_or_404(product_id)

    recommendations = get_recommendations(product_id)

    return render_template(
        "product_detail.html",
        product=product,
        recommendations=recommendations
    )


# =========================
# ADD DEMO PRODUCTS
# =========================

@app.route("/add-products")
def add_products():

    # Check if products already exist
    if Product.query.count() > 0:
        return "Products already exist!"

    products = [

        Product(
            name="Wireless Headphones",
            description="Premium wireless headphones with clear sound and comfortable design.",
            price=5999,
            category="Electronics",
            image="headphones.jpg",
            stock=25
        ),

        Product(
            name="Smart Watch",
            description="Modern smartwatch with fitness tracking and health features.",
            price=7499,
            category="Electronics",
            image="smartwatch.jpg",
            stock=15
        ),

        Product(
            name="Running Shoes",
            description="Comfortable lightweight running shoes for everyday use.",
            price=6499,
            category="Fashion",
            image="shoes.jpg",
            stock=20
        ),

        Product(
            name="Laptop Backpack",
            description="Durable laptop backpack with multiple compartments.",
            price=3299,
            category="Accessories",
            image="backpack.jpg",
            stock=30
        ),

        Product(
            name="Classic Hoodie",
            description="Comfortable casual hoodie made for everyday wear.",
            price=3999,
            category="Fashion",
            image="hoodie.jpg",
            stock=18
        ),

        Product(
            name="Coffee Maker",
            description="Easy-to-use coffee maker for delicious coffee at home.",
            price=8999,
            category="Home",
            image="coffee-maker.jpg",
            stock=10
        )
    ]

    db.session.add_all(products)
    db.session.commit()

    return "6 demo products added successfully! 🎉"


# =========================
# ADD TO CART
# =========================

@app.route("/add-to-cart/<int:product_id>")
def add_to_cart(product_id):

    product = Product.query.get_or_404(product_id)

    cart = session.get("cart", {})

    product_id = str(product.id)

    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    session["cart"] = cart
    session.modified = True

    return redirect(url_for("cart"))


# =========================
# CART PAGE
# =========================

@app.route("/cart")
def cart():

    cart = session.get("cart", {})

    cart_products = []
    total = 0

    for product_id, quantity in cart.items():

        product = Product.query.get(int(product_id))

        if product:

            item_total = product.price * quantity

            total += item_total

            cart_products.append({
                "product": product,
                "quantity": quantity,
                "item_total": item_total
            })

    return render_template(
        "cart.html",
        cart_products=cart_products,
        total=total
    )
# =========================
# CHECKOUT PAGE
# =========================

@app.route("/checkout", methods=["GET", "POST"])
def checkout():

    cart = session.get("cart", {})

    if not cart:
        return redirect(url_for("cart"))

    cart_products = []
    total = 0

    for product_id, quantity in cart.items():

        product = Product.query.get(int(product_id))

        if product:

            item_total = product.price * quantity
            total += item_total

            cart_products.append({
                "product": product,
                "quantity": quantity,
                "item_total": item_total
            })

    if request.method == "POST":

        customer_name = request.form["customer_name"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]
        city = request.form["city"]
        payment_method = request.form["payment_method"]

        order = Order(
            customer_name=customer_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            payment_method=payment_method,
            total=total
        )

        db.session.add(order)
        db.session.commit()

        session["cart"] = {}
        session.modified = True

        return render_template(
            "order_success.html",
            order=order
        )

    return render_template(
        "checkout.html",
        cart_products=cart_products,
        total=total
    )

    cart = session.get("cart", {})

    if not cart:
        return redirect(url_for("cart"))

    cart_products = []
    total = 0

    for product_id, quantity in cart.items():

        product = Product.query.get(int(product_id))

        if product:

            item_total = product.price * quantity
            total += item_total

            cart_products.append({
                "product": product,
                "quantity": quantity,
                "item_total": item_total
            })

    return render_template(
        "checkout.html",
        cart_products=cart_products,
        total=total
    )


# =========================
# INCREASE QUANTITY
# =========================

@app.route("/cart/increase/<int:product_id>")
def increase_cart(product_id):

    cart = session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1

    session["cart"] = cart
    session.modified = True

    return redirect(url_for("cart"))


# =========================
# DECREASE QUANTITY
# =========================

@app.route("/cart/decrease/<int:product_id>")
def decrease_cart(product_id):

    cart = session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:

        cart[product_id] -= 1

        if cart[product_id] <= 0:
            del cart[product_id]

    session["cart"] = cart
    session.modified = True

    return redirect(url_for("cart"))


# =========================
# REMOVE FROM CART
# =========================

@app.route("/cart/remove/<int:product_id>")
def remove_from_cart(product_id):

    cart = session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    session["cart"] = cart
    session.modified = True

    return redirect(url_for("cart"))


# =========================
## =========================
# =========================
# SHOPPING AI CHATBOT
# =========================

@app.route("/shopping-ai", methods=["POST"])
def shopping_ai():

    message = request.json.get("message", "").strip()
    message_lower = message.lower()

    # Empty message
    if not message:
        return {
            "reply": "Please tell me what you are looking for 😊",
            "products": []
        }

    # =========================
    # PRODUCT COMPARISON
    # =========================

    if "compare" in message_lower:

        comparison_products = compare_products(message)

        if len(comparison_products) >= 2:

            product1 = comparison_products[0]
            product2 = comparison_products[1]

            reply = (
                f"🔍 Here's your comparison:\n\n"
                f"🛍️ {product1.name}\n"
                f"💰 Price: Rs. {product1.price}\n"
                f"📂 Category: {product1.category}\n"
                f"📦 Stock: {product1.stock}\n\n"
                f"VS\n\n"
                f"🛍️ {product2.name}\n"
                f"💰 Price: Rs. {product2.price}\n"
                f"📂 Category: {product2.category}\n"
                f"📦 Stock: {product2.stock}"
            )

            return {
                "reply": reply,
                "products": []
            }

        return {
            "reply": (
                "🤖 I can compare two products for you. "
                "Try: compare Wireless Headphones and Smart Watch"
            ),
            "products": []
        }

    # =========================
    # CONVERSATIONAL RESPONSES
    # =========================

    if any(
        word in message_lower.split()
        for word in ["hi", "hello", "hey"]
    ):

        return {
            "reply": "Hello! 👋 Welcome to ShopSphere AI. What are you looking for today?",
            "products": []
        }

    if "thank" in message_lower:

        return {
            "reply": "You're welcome! 😊 Happy shopping!",
            "products": []
        }

    if any(
        word in message_lower
        for word in ["bye", "goodbye"]
    ):

        return {
            "reply": "Goodbye! 👋 Come back soon to ShopSphere!",
            "products": []
        }

    if any(
        word in message_lower
        for word in ["recommend", "suggest"]
    ):

        return {
            "reply": "Sure! 😊 Tell me your preferred category or budget and I'll recommend some products for you.",
            "products": []
        }

    # =========================
    # PRODUCT SEARCH
    # =========================

    products = shopping_assistant(message)

    product_data = []

    for product in products:

        product_data.append({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "category": product.category,
            "image": product.image
        })

    # =========================
    # PRODUCT RESPONSE
    # =========================

    if products:

        reply = "✨ I found these products for you:"

    else:

        reply = (
            "😔 Sorry, I couldn't find a suitable product. "
            "Try another product, category or budget."
        )

    return {
        "reply": reply,
        "products": product_data
    } 
# CREATE DATABASE
# =========================

with app.app_context():
    db.create_all()


# =========================
# RUN APP
# =========================

if __name__ == "__main__":
    app.run(debug=True)