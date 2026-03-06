# 🛒 Local Marketplace

A hyperlocal e-commerce platform for 3–4 blocks in one district.
Single admin, multiple customers, COD delivery with zone-based charges.

---

## 🚀 Tech Stack

| Layer      | Tech                          |
|------------|-------------------------------|
| Frontend   | Vue 3 + Vite + Tailwind CSS   |
| Backend    | FastAPI + SQLAlchemy          |
| Database   | MySQL (PlanetScale)           |
| Images     | Cloudinary                    |
| Frontend Hosting | Vercel               |
| Backend Hosting  | Render               |

---

## 📁 Project Structure

```
local-marketplace/
├── frontend/          → Vue 3 app
├── backend/           → FastAPI app
└── database/
    └── schema.sql     → Full MySQL schema + seed data
```

---

## ⚙️ Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- MySQL 8.0 (local) or PlanetScale account

---

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure env
cp .env.example .env
# Edit .env with your DB credentials

# Run migrations / create tables (auto on startup)
python seed.py              # Seeds admin user, blocks, categories

# Start development server
uvicorn app.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

---

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy and configure env
cp .env.example .env
# Set VITE_API_BASE_URL=http://localhost:8000/api/v1

# Start dev server
npm run dev
```

Frontend at: http://localhost:5173

---

## 🗄️ Database Setup

### Option A: PlanetScale (Production)
1. Create account at planetscale.com
2. Create a new database: `local_marketplace`
3. Go to "Connect" → copy the connection string
4. Set `DATABASE_URL` in backend `.env`
5. Run `python seed.py` to populate initial data

### Option B: Local MySQL
```sql
CREATE DATABASE local_marketplace;
-- Run database/schema.sql
```

---

## 🔑 Default Admin Credentials

```
Email:    admin@localmart.com
Password: admin123
```
**⚠️ Change this immediately in production!**

---

## 🌐 Deployment

### Frontend → Vercel

```bash
cd frontend
npm run build

# Or connect GitHub repo to Vercel
# Set environment variable:
# VITE_API_BASE_URL = https://your-backend.onrender.com/api/v1
```

### Backend → Render

1. Create new Web Service on render.com
2. Connect your GitHub repo
3. Set:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add all environment variables from `.env.example`

### Environment Variables for Production

**Backend (Render):**
```
APP_NAME=Local Marketplace
SECRET_KEY=<generate: python -c "import secrets; print(secrets.token_hex(32))">
DATABASE_URL=mysql+pymysql://user:pass@host/db?ssl_ca=/etc/ssl/certs/ca-certificates.crt
CLOUDINARY_CLOUD_NAME=xxx
CLOUDINARY_API_KEY=xxx
CLOUDINARY_API_SECRET=xxx
CORS_ORIGINS=https://your-app.vercel.app
ENVIRONMENT=production
```

**Frontend (Vercel):**
```
VITE_API_BASE_URL=https://your-backend.onrender.com/api/v1
VITE_APP_NAME=Local Mart
```

---

## 📡 API Reference

### Auth
```
POST  /api/v1/auth/register
POST  /api/v1/auth/login
GET   /api/v1/auth/me
PUT   /api/v1/auth/profile
PUT   /api/v1/auth/change-password
```

### Public
```
GET   /api/v1/products            ?search=&category=&min_price=&max_price=&page=&limit=
GET   /api/v1/products/featured
GET   /api/v1/products/:slug
GET   /api/v1/categories
GET   /api/v1/blocks
GET   /api/v1/blocks/:id/zones
```

### Customer (JWT Required)
```
GET/POST/PUT/DELETE   /api/v1/addresses
PATCH /api/v1/addresses/:id/set-default
GET   /api/v1/cart
POST  /api/v1/cart/items
PUT   /api/v1/cart/items/:product_id
DELETE /api/v1/cart/items/:product_id
DELETE /api/v1/cart/clear
GET   /api/v1/delivery/calculate?address_id=
POST  /api/v1/orders/checkout
GET   /api/v1/orders
GET   /api/v1/orders/:id
POST  /api/v1/reviews
```

### Admin (JWT + Admin Role Required)
```
GET   /api/v1/admin/dashboard
GET/PATCH /api/v1/admin/orders
POST  /api/v1/admin/blocks
POST  /api/v1/blocks/zones
POST/PUT/DELETE /api/v1/products
POST/PUT/DELETE /api/v1/categories
```

---

## 🔒 Security Notes

- JWT tokens expire in 7 days
- Passwords hashed with bcrypt (cost 12)
- CORS restricted to frontend domain only
- Rate limiting on login endpoint (5 req/min)
- All product/address data snapshotted in orders
- Input validation via Pydantic on all endpoints
- Admin routes double-guarded (JWT + role check)

---

## 💰 Infrastructure Cost

| Service     | Plan          | Cost    |
|-------------|---------------|---------|
| Vercel      | Hobby         | Free    |
| Render      | Starter       | $7/mo   |
| PlanetScale | Hobby         | Free    |
| Cloudinary  | Free          | Free    |
| **Total**   |               | **~$7/mo** |

---

## 🗺️ Phase 2 Roadmap

- OTP phone verification (MSG91/Twilio)
- UPI/Razorpay payment integration
- SMS/WhatsApp order notifications
- Coupon codes and discounts
- Wishlist feature
- PWA (installable mobile app)
- Delivery person role
- CSV product bulk import
- Customer order cancellation
