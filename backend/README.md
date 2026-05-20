# 🏪 Mini Market POS — Backend

Django 5.x + DRF + PostgreSQL + Redis + Celery

## 🚀 Tez boshlash

### 1. Repo clone va virtual muhit

```bash
git clone <repo>
cd minimarket/backend

python -m venv venv
source venv/bin/activate          # Linux/Mac
# venv\Scripts\activate           # Windows

pip install -r requirements/development.txt
```

### 2. .env fayl

```bash
cp .env.example .env
# .env ni o'zingizga moslashtiring
```

### 3. PostgreSQL va Redis (Docker bilan)

```bash
# Loyiha root papkasida
cd ..
docker-compose up -d db redis
```

### 4. Migratsiya va superuser

```bash
cd backend
python manage.py migrate
python manage.py createsuperuser
```

### 5. Serverni ishga tushirish

```bash
python manage.py runserver
```

## 🧪 Testlar

```bash
# Barcha testlar
pytest

# Faqat users testlari
pytest apps/users/tests/ -v

# Coverage bilan
pytest --cov=apps --cov-report=html
```

## 📚 API Docs

Server ishlagandan keyin:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc:      http://localhost:8000/api/redoc/

## 🗂️ Struktura

```
backend/
├── config/
│   ├── settings/
│   │   ├── base.py          ← umumiy sozlamalar
│   │   ├── development.py   ← local muhit
│   │   ├── production.py    ← ishchi muhit
│   │   └── test.py          ← pytest uchun
│   ├── urls.py
│   └── celery.py
│
├── apps/
│   ├── core/                ← BaseModel, pagination, exceptions
│   └── users/               ← CustomUser, JWT auth
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       ├── services.py      ← biznes logika
│       ├── urls.py
│       └── tests/
│           ├── factories.py
│           ├── test_models.py
│           ├── test_auth.py
│           ├── test_views.py
│           └── test_services.py
│
└── requirements/
    ├── base.txt
    ├── development.txt
    └── production.txt
```

## 📋 Keyingi qadam

- [ ] `products` app — Category, Unit, Product, Barcode
- [ ] `companies` app — Company, Branch
- [ ] `inventory` app — Stock, StockMovement
- [ ] `purchases` app — Purchase, PurchaseItem
- [ ] `sales` app — Sale, SaleItem, Payment (Cart)
- [ ] `history` app — AuditLog
- [ ] `reports` app — PDF/Excel export

## 🔑 API Endpoints (users)

| Method | URL | Tavsif | Ruxsat |
|--------|-----|--------|--------|
| POST | `/api/v1/auth/login/` | Login | Barchasi |
| POST | `/api/v1/auth/token/refresh/` | Token yangilash | Barchasi |
| POST | `/api/v1/auth/logout/` | Logout | Auth |
| GET | `/api/v1/auth/users/` | Userlar ro'yxati | Admin+ |
| POST | `/api/v1/auth/users/` | User yaratish | Admin+ |
| GET | `/api/v1/auth/users/{id}/` | User detail | Admin+ |
| PUT | `/api/v1/auth/users/{id}/` | User yangilash | Admin+ |
| DELETE | `/api/v1/auth/users/{id}/` | User o'chirish | Admin+ |
| POST | `/api/v1/auth/users/{id}/reset-password/` | Parol reset | SuperAdmin |
| GET | `/api/v1/auth/me/profile/` | O'z profili | Auth |
| PATCH | `/api/v1/auth/me/update_profile/` | Profilni tahrirlash | Auth |
| POST | `/api/v1/auth/me/change-password/` | Parol almashtirish | Auth |
