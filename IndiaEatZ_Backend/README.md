# IndiaEatZ – Python Flask Demo Backend

A frontend-independent REST API for the IndiaEatZ food-ordering demo. It uses Flask, MongoDB and JSON. It contains no React, HTML templates or CSS.

## 1. Requirements
- Python 3.10+
- MongoDB Community Server running locally, or a MongoDB Atlas connection string
- pip

## 2. Install and run (Windows PowerShell)

Open a terminal in this project folder:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` if your MongoDB URI or demo admin credentials are different.

Make sure MongoDB is running, then load sample products and the demo admin:

```powershell
python seed.py
```

Start the API:

```powershell
python app.py
```

Open `http://127.0.0.1:5000/` or `http://127.0.0.1:5000/api/health`.

### CMD alternative
```bat
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python seed.py
python app.py
```

## 3. Demo admin login
- Email: `admin@indiaeatz.demo`
- Password: `Admin@123`

Change these in `.env` for your own local demo. Do not use demo credentials or Flask debug mode in production.

## 4. API endpoints

All request and response bodies are JSON. Protected routes require:
`Authorization: Bearer YOUR_TOKEN`

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| GET | `/api/health` | Public | API and MongoDB health |
| POST | `/api/auth/register` | Public | Register customer |
| POST | `/api/auth/login` | Public | Login |
| GET | `/api/auth/me` | Login | Current user |
| GET | `/api/products` | Public | List products |
| GET | `/api/products?category=Veg` | Public | Filter category |
| GET | `/api/products?search=paneer` | Public | Search products |
| GET | `/api/products/categories` | Public | Category list |
| GET | `/api/products/<id>` | Public | Product detail |
| GET | `/api/cart` | Login | View cart |
| POST | `/api/cart/items` | Login | Add item |
| PATCH | `/api/cart/items/<product_id>` | Login | Set quantity; zero removes |
| DELETE | `/api/cart/items/<product_id>` | Login | Remove item |
| DELETE | `/api/cart` | Login | Clear cart |
| POST | `/api/orders` | Login | Place order from cart |
| GET | `/api/orders` | Login | Customer order history |
| GET | `/api/orders/<id>` | Login | Customer order detail |
| POST | `/api/admin/products` | Admin | Create product |
| PUT | `/api/admin/products/<id>` | Admin | Edit product |
| DELETE | `/api/admin/products/<id>` | Admin | Delete product |
| GET | `/api/admin/orders` | Admin | View all orders |
| PATCH | `/api/admin/orders/<id>/status` | Admin | Update order status |

Categories: `Street Food`, `Cold Drinks`, `Veg`, `Non-Veg`.

Order statuses: `Placed`, `Confirmed`, `Preparing`, `Out for delivery`, `Delivered`, `Cancelled`.

## 5. Example requests

### Register a customer
```json
POST /api/auth/register
{
  "name": "Asha",
  "email": "asha@example.com",
  "password": "secret123"
}
```

### Login
```json
POST /api/auth/login
{
  "email": "asha@example.com",
  "password": "secret123"
}
```
Copy `data.token` from the response and send it as a Bearer token on protected routes.

### Add a product (admin token required)
```json
POST /api/admin/products
{
  "name": "Misal Pav",
  "category": "Street Food",
  "price": 80,
  "description": "Spicy Maharashtrian misal.",
  "image_url": ""
}
```

### Add item to cart
```json
POST /api/cart/items
{
  "product_id": "PASTE_PRODUCT_ID_HERE",
  "quantity": 2
}
```

### Place an order
```json
POST /api/orders
{
  "payment_method": "demo",
  "simulate_payment": true
}
```
This only records a simulated payment status in MongoDB. It does not connect to a payment gateway, charge a card, or transfer money.

### Update order status (admin token required)
```json
PATCH /api/admin/orders/PASTE_ORDER_ID_HERE/status
{
  "status": "Preparing"
}
```

## 6. Connect any frontend
Call the API from any frontend using HTTP `fetch`, Axios, or another HTTP client. For example:

```javascript
const response = await fetch("http://127.0.0.1:5000/api/products");
const result = await response.json();
console.log(result.data.products);
```

For protected endpoints, include:
```javascript
headers: {
  "Content-Type": "application/json",
  "Authorization": `Bearer ${token}`
}
```

Set `CORS_ORIGINS` in `.env` to your frontend origin(s) when moving beyond local development.

## 7. Folder structure

```text
IndiaEatZ_Backend/
├── app.py
├── config.py
├── extensions.py
├── seed.py
├── requirements.txt
├── .env.example
├── README.md
├── routes/
│   ├── auth.py
│   ├── products.py
│   ├── cart.py
│   ├── orders.py
│   └── admin.py
└── utils/
    ├── auth.py
    ├── responses.py
    └── serializers.py
```

## 8. Demo limitations and production notes
- This is a learning/demo backend, not a production-ready food delivery platform.
- Payment is simulated only. Never collect or store card details here.
- The demo uses signed bearer tokens and password hashing. Add HTTPS, stronger secret management, rate limiting, input validation, logging, tests and production deployment settings before launch.
- Cart prices are copied when an item is added. For a real checkout, re-fetch current product prices and validate stock server-side before accepting an order.
- Admin creation is seeded from `.env`; public registration always creates customer accounts.
