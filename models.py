from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(300), nullable=True)
    stock = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Product {self.name}>"


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    customer_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)

    payment_method = db.Column(db.String(50), nullable=False)

    total = db.Column(db.Float, nullable=False)

    status = db.Column(
        db.String(50),
        default="Pending"
    )

    def __repr__(self):
        return f"<Order {self.id}>"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        default="customer"
    )

    def __repr__(self):
        return f"<User {self.username}>"