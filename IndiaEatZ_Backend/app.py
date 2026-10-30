from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from extensions import mongo
from routes.auth import auth_bp
from routes.products import products_bp
from routes.cart import cart_bp
from routes.orders import orders_bp
from routes.admin import admin_bp
from utils.responses import error

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})
    mongo.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(products_bp, url_prefix="/api/products")
    app.register_blueprint(cart_bp, url_prefix="/api/cart")
    app.register_blueprint(orders_bp, url_prefix="/api/orders")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    @app.get("/")
    def home():
        return jsonify({
            "name": "IndiaEatZ API",
            "message": "Backend is running",
            "version": "1.0.0",
            "health": "/api/health"
        })

    @app.get("/api/health")
    def health():
        try:
            mongo.db.command("ping")
            return jsonify({"status": "ok", "database": "connected"})
        except Exception as exc:
            return jsonify({"status": "degraded", "database": "disconnected",
                            "detail": str(exc)}), 503

    @app.errorhandler(404)
    def not_found(_):
        return error("Endpoint not found", 404)

    @app.errorhandler(500)
    def server_error(_):
        return error("Internal server error", 500)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=app.config["PORT"], debug=app.config["DEBUG"])
