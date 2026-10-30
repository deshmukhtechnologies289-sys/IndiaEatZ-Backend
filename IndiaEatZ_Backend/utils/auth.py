from functools import wraps
from flask import request, current_app, g
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from bson import ObjectId
from extensions import mongo
from utils.responses import error

def make_token(user_id):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="indiaeatz-auth")
    return serializer.dumps(str(user_id))

def decode_token(token):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="indiaeatz-auth")
    return serializer.loads(token, max_age=current_app.config["TOKEN_MAX_AGE"])

def require_auth(admin=False):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            header = request.headers.get("Authorization", "")
            if not header.startswith("Bearer "):
                return error("Authorization token required", 401)
            try:
                user_id = decode_token(header.split(" ", 1)[1])
                user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
            except (BadSignature, SignatureExpired, ValueError):
                return error("Invalid or expired token", 401)
            if not user:
                return error("User not found", 401)
            if admin and user.get("role") != "admin":
                return error("Admin access required", 403)
            g.current_user = user
            return fn(*args, **kwargs)
        return wrapper
    return decorator
