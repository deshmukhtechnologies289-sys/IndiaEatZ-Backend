"""Insert demo products and create/update the demo admin account."""
from werkzeug.security import generate_password_hash
from app import app
from extensions import mongo
from datetime import datetime

PRODUCTS = [
    {"name": "Pani Puri", "category": "Street Food", "price": 40, "description": "Crispy puris with spicy and tangy water."},
    {"name": "Vada Pav", "category": "Street Food", "price": 30, "description": "Mumbai-style potato fritter bun."},
    {"name": "Pav Bhaji", "category": "Street Food", "price": 90, "description": "Buttery pav served with vegetable bhaji."},
    {"name": "Fresh Lime Soda", "category": "Cold Drinks", "price": 50, "description": "Refreshing lime soda."},
    {"name": "Mango Juice", "category": "Cold Drinks", "price": 60, "description": "Chilled mango drink."},
    {"name": "Veg Biryani", "category": "Veg", "price": 130, "description": "Fragrant rice with vegetables and spices."},
    {"name": "Paneer Tikka", "category": "Veg", "price": 160, "description": "Grilled marinated paneer."},
    {"name": "Chicken Biryani", "category": "Non-Veg", "price": 180, "description": "Aromatic chicken biryani."},
    {"name": "Chicken 65", "category": "Non-Veg", "price": 150, "description": "Spicy fried chicken bites."}
]

with app.app_context():
    for product in PRODUCTS:
        mongo.db.products.update_one({"name": product["name"]}, {"$setOnInsert": {
            **product, "image_url": "", "is_available": True, "created_at": datetime.utcnow()
        }}, upsert=True)
    email = app.config["ADMIN_EMAIL"].lower()
    mongo.db.users.update_one({"email": email}, {"$set": {
        "name": "IndiaEatZ Demo Admin", "email": email,
        "password_hash": generate_password_hash(app.config["ADMIN_PASSWORD"]),
        "role": "admin"
    }}, upsert=True)
    print("Demo data ready.")
    print("Admin email:", email)
    print("Admin password:", app.config["ADMIN_PASSWORD"])
