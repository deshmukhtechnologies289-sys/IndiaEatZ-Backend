from flask import Blueprint, request, g
from bson import ObjectId
from extensions import mongo
from utils.auth import require_auth
from utils.responses import error, success
from utils.serializers import serialize_doc

cart_bp = Blueprint("cart", __name__)

@cart_bp.get("")
@require_auth()
def get_cart():
    cart = mongo.db.carts.find_one({"user_id": g.current_user["_id"]}) or {"items": []}
    return success("Cart fetched", {"cart": serialize_doc(cart) if cart.get("_id") else cart})

@cart_bp.post("/items")
@require_auth()
def add_item():
    data = request.get_json(silent=True) or {}
    try:
        product_id, quantity = ObjectId(data.get("product_id", "")), int(data.get("quantity", 1))
    except Exception:
        return error("Valid product_id and quantity are required")
    if quantity < 1:
        return error("Quantity must be at least 1")
    product = mongo.db.products.find_one({"_id": product_id, "is_available": {"$ne": False}})
    if not product:
        return error("Product not found", 404)
    cart = mongo.db.carts.find_one({"user_id": g.current_user["_id"]}) or {"user_id": g.current_user["_id"], "items": []}
    items = cart["items"]
    found = next((item for item in items if item["product_id"] == product_id), None)
    if found:
        found["quantity"] += quantity
    else:
        items.append({"product_id": product_id, "name": product["name"], "price": float(product["price"]), "quantity": quantity})
    mongo.db.carts.update_one({"user_id": g.current_user["_id"]}, {"$set": {"items": items}}, upsert=True)
    return success("Item added to cart", {"items": [{"product_id": str(i["product_id"]), "name": i["name"], "price": i["price"], "quantity": i["quantity"]} for i in items]})

@cart_bp.patch("/items/<product_id>")
@require_auth()
def update_item(product_id):
    data = request.get_json(silent=True) or {}
    try:
        pid, quantity = ObjectId(product_id), int(data.get("quantity", 0))
    except Exception:
        return error("Invalid product ID or quantity")
    cart = mongo.db.carts.find_one({"user_id": g.current_user["_id"]})
    if not cart:
        return error("Cart is empty", 404)
    if quantity <= 0:
        cart["items"] = [i for i in cart["items"] if i["product_id"] != pid]
    else:
        item = next((i for i in cart["items"] if i["product_id"] == pid), None)
        if not item:
            return error("Item not found in cart", 404)
        item["quantity"] = quantity
    mongo.db.carts.update_one({"_id": cart["_id"]}, {"$set": {"items": cart["items"]}})
    return success("Cart updated")

@cart_bp.delete("/items/<product_id>")
@require_auth()
def remove_item(product_id):
    try:
        pid = ObjectId(product_id)
    except Exception:
        return error("Invalid product ID")
    mongo.db.carts.update_one({"user_id": g.current_user["_id"]}, {"$pull": {"items": {"product_id": pid}}})
    return success("Item removed from cart")

@cart_bp.delete("")
@require_auth()
def clear_cart():
    mongo.db.carts.update_one({"user_id": g.current_user["_id"]}, {"$set": {"items": []}}, upsert=True)
    return success("Cart cleared")
