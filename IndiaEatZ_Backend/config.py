import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-demo-secret-before-deployment")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/indiaeatz")
    PORT = int(os.getenv("PORT", "5000"))
    DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
    TOKEN_MAX_AGE = int(os.getenv("TOKEN_MAX_AGE", "86400"))
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@indiaeatz.demo")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin@123")
