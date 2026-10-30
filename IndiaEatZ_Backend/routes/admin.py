from flask import Blueprint, request
from datetime import datetime
from bson import ObjectId
from extensions import mongo
from utils.auth import require_auth
from utils.responses import error, success
from utils.serializers import serialize_doc

admin_bp = Blueprint("admin", __name__)
VALID_CATEGORIES = ["Street Food", "Cold Drinks", "Veg", "Non-Veg"]
VALID_STATUSES = ["Placed", "Confirmed", "Preparing", "Out for delivery", "Delivered", "Cancelled"]

@admin_bp.post("/products")
@require_auth(admin=True)
def create_product():
    data = request.get_json(silent=True) or {}
    required = ["name", "category", "price"]
    if any(data.get(k) in (None, "") for k in required):
        return error("name, category and price are required")
    if data["category"] not in VALID_CATEGORIES:
        return error("Invalid category")
    try:
        price = float(data["price"])
        if price < 0: raise ValueError()
    except Exception:
        return error("price must be a non-negative number")
    product = {"name": data["name"].strip(), "category": data["category"],
               "price": price, "description": data.get("description", ""),
               "image_url": data.get("image_url", ""),
               "is_available": bool(data.get("is_available", True)),
               "created_at": datetime.utcnow()}
    product["_id"] = mongo.db.products.insert_one(product).inserted_id
    return success("Product created", {"product": serialize_doc(product)}, 201)

@admin_bp.put("/products/<product_id>")
@require_auth(admin=True)
def edit_product(product_id):
    try: oid = ObjectId(product_id)
    except Exception: return error("Invalid product ID")
    data = request.get_json(silent=True) or {}
    allowed = {"name", "category", "price", "description", "image_url", "is_available"}
    update = {k: v for k, v in data.items() if k in allowed}
    if not update: return error("No editable fields supplied")
    if "category" in update and update["category"] not in VALID_CATEGORIES: return error("Invalid category")
    if "price" in update:
        try:
            update["price"] = float(update["price"])
            if update["price"] < 0: raise ValueError()
        except Exception: return error("price must be a non-negative number")
    result = mongo.db.products.update_one({"_id": oid}, {"$set": update})
    if not result.matched_count: return error("Product not found", 404)
    return success("Product updated")

@admin_bp.delete("/products/<product_id>")
@require_auth(admin=True)
def delete_product(product_id):
    try: oid = ObjectId(product_id)
    except Exception: return error("Invalid product ID")
    result = mongo.db.products.delete_one({"_id": oid})
    if not result.deleted_count: return error("Product not found", 404)
    return success("Product deleted")

@admin_bp.patch("/orders/<order_id>/status")
@require_auth(admin=True)
def update_order_status(order_id):
    try: oid = ObjectId(order_id)
    except Exception: return error("Invalid order ID")
    status = (request.get_json(silent=True) or {}).get("status")
    if status not in VALID_STATUSES:
        return error("Invalid status", valid_statuses=VALID_STATUSES)
    result = mongo.db.orders.update_one({"_id": oid}, {"$set": {"status": status, "updated_at": datetime.utcnow()}})
    if not result.matched_count: return error("Order not found", 404)
    return success("Order status updated", {"status": status})

@admin_bp.get("/orders")
@require_auth(admin=True)
def all_orders():
    orders = [serialize_doc(o) for o in mongo.db.orders.find().sort("created_at", -1)]
    return success("All orders fetched", {"orders": orders})
