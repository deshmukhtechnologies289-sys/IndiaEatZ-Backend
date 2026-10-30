from flask import Blueprint, request, g
from datetime import datetime
from bson import ObjectId
from extensions import mongo
from utils.auth import require_auth
from utils.responses import error, success
from utils.serializers import serialize_doc

orders_bp = Blueprint("orders", __name__)
STATUSES = ["Placed", "Confirmed", "Preparing", "Out for delivery", "Delivered", "Cancelled"]

@orders_bp.post("")
@require_auth()
def place_order():
    data = request.get_json(silent=True) or {}
    cart = mongo.db.carts.find_one({"user_id": g.current_user["_id"]})
    items = cart.get("items", []) if cart else []
    if not items:
        return error("Your cart is empty")
    subtotal = round(sum(i["price"] * i["quantity"] for i in items), 2)
    # Demo-only payment simulation; no payment gateway or money transfer.
    payment_method = data.get("payment_method", "demo")
    payment_status = "Demo paid" if data.get("simulate_payment", True) else "Pending"
    order = {
        "user_id": g.current_user["_id"],
        "customer_name": g.current_user["name"],
        "items": [{"product_id": str(i["product_id"]), "name": i["name"], "price": i["price"], "quantity": i["quantity"]} for i in items],
        "subtotal": subtotal, "total": subtotal,
        "status": "Placed", "payment_method": payment_method,
        "payment_status": payment_status, "created_at": datetime.utcnow()
    }
    result = mongo.db.orders.insert_one(order)
    mongo.db.carts.update_one({"user_id": g.current_user["_id"]}, {"$set": {"items": []}})
    order["_id"] = result.inserted_id
    return success("Order placed successfully (demo)", {"order": serialize_doc(order)}, 201)

@orders_bp.get("")
@require_auth()
def order_history():
    orders = [serialize_doc(o) for o in mongo.db.orders.find({"user_id": g.current_user["_id"]}).sort("created_at", -1)]
    return success("Order history fetched", {"orders": orders})

@orders_bp.get("/<order_id>")
@require_auth()
def get_order(order_id):
    try:
        oid = ObjectId(order_id)
    except Exception:
        return error("Invalid order ID")
    order = mongo.db.orders.find_one({"_id": oid, "user_id": g.current_user["_id"]})
    if not order:
        return error("Order not found", 404)
    return success("Order fetched", {"order": serialize_doc(order)})
