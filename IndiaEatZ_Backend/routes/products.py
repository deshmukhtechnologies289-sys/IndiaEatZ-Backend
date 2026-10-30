from flask import Blueprint, request
from extensions import mongo
from utils.responses import error, success
from utils.serializers import serialize_doc

products_bp = Blueprint("products", __name__)
CATEGORIES = ["Street Food", "Cold Drinks", "Veg", "Non-Veg"]

@products_bp.get("")
def list_products():
    query = {"is_available": {"$ne": False}}
    category = request.args.get("category")
    search = request.args.get("search", "").strip()
    if category:
        query["category"] = category
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"category": {"$regex": search, "$options": "i"}}
        ]
    products = [serialize_doc(p) for p in mongo.db.products.find(query).sort("name", 1)]
    return success("Products fetched", {"products": products, "count": len(products), "categories": CATEGORIES})

@products_bp.get("/categories")
def categories():
    return success("Categories fetched", {"categories": CATEGORIES})

@products_bp.get("/<product_id>")
def get_product(product_id):
    from bson import ObjectId
    try:
        product = mongo.db.products.find_one({"_id": ObjectId(product_id), "is_available": {"$ne": False}})
    except Exception:
        return error("Invalid product ID", 400)
    if not product:
        return error("Product not found", 404)
    return success("Product fetched", {"product": serialize_doc(product)})
