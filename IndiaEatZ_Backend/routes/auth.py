from flask import Blueprint, request
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import mongo
from utils.auth import make_token, require_auth
from utils.responses import error, success
from utils.serializers import public_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    name, email, password = data.get("name", "").strip(), data.get("email", "").strip().lower(), data.get("password", "")
    if not name or not email or len(password) < 6:
        return error("Name, valid email and password (minimum 6 characters) are required")
    if mongo.db.users.find_one({"email": email}):
        return error("Email is already registered", 409)
    user_id = mongo.db.users.insert_one({
        "name": name, "email": email,
        "password_hash": generate_password_hash(password),
        "role": "customer", "created_at": __import__("datetime").datetime.utcnow()
    }).inserted_id
    user = mongo.db.users.find_one({"_id": user_id})
    return success("Registration successful", {"user": public_user(user), "token": make_token(user_id)}, 201)

@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email, password = data.get("email", "").strip().lower(), data.get("password", "")
    user = mongo.db.users.find_one({"email": email})
    if not user or not check_password_hash(user.get("password_hash", ""), password):
        return error("Invalid email or password", 401)
    return success("Login successful", {"user": public_user(user), "token": make_token(user["_id"])})

@auth_bp.get("/me")
@require_auth()
def me():
    from flask import g
    return success("Current user", {"user": public_user(g.current_user)})
