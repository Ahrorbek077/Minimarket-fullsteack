# Minimarket — Vultr VPS Deploy Qo'llanmasi

## Loyiha tuzilishi
```
minimarket/
├── backend/          ← Django + DRF + Celery
├── frontend/         ← Next.js 16 + React 19
├── docker-compose.prod.yml   ← Production compose
├── frontend.Dockerfile       ← Next.js uchun Dockerfile
├── .env.production           ← Sozlamalar (to'ldiring!)
└── nginx/
    ├── nginx.conf
    └── conf.d/minimarket.conf
```

---

## QADAM 1 — Kodni tuzatish (local kompyuterda)

### 1.1 proxy.ts → middleware.ts
`frontend/src/proxy.ts` faylini `frontend/src/middleware.ts` ga **rename** qiling
va ichidagi `proxy` funksiyasini `middleware` ga o'zgartiring.

Yoki bu fayldagi `middleware.ts` ni `frontend/src/` ga ko'chiring (eski proxy.ts ni o'chiring).

### 1.2 next.config.ts
`frontend/next.config.ts` ga `output: "standalone"` qo'shing.
Tayyor fayl: `next.config.ts` (bu papkada)

### 1.3 Fayllarni joylashtirish
```
minimarket/
├── frontend.Dockerfile    ← bu papkadagi faylni ko'chiring
├── docker-compose.prod.yml
├── nginx/
└── ...
```

---

## QADAM 2 — VPS tayyorlash

### Vultr dan VPS oling:
- OS: Ubuntu 22.04 LTS
- Plan: 2 CPU, 4GB RAM minimum (yoki 2GB ham ishlaydi)
- Location: yaqin region

### VPS ga kiring va setup skriptni ishga tushiring:
```bash
ssh root@YOUR_VPS_IP
curl -o setup.sh https://raw.githubusercontent.com/.../setup-vps.sh
# Yoki faylni SCP bilan ko'chiring:
scp scripts/setup-vps.sh root@YOUR_VPS_IP:/root/
bash /root/setup-vps.sh
```

---

## QADAM 3 — Loyihani serverga ko'chirish

```bash
# Local kompyuterda:
scp -r minimarket/ root@YOUR_VPS_IP:/opt/minimarket/
```

---

## QADAM 4 — .env.production to'ldirish

Serverda:
```bash
nano /opt/minimarket/.env.production
```

**O'zgartiring:**
- `CHANGE_THIS_TO_RANDOM_50_CHARS_STRING` → tasodifiy kalit
  ```bash
  python3 -c "import secrets; print(secrets.token_urlsafe(50))"
  ```
- `YOUR_DOMAIN.COM` → sizning domeningiz (yoki VPS IP)
- `CHANGE_THIS_STRONG_PASSWORD` → kuchli parol
- `YOUR_VPS_IP` → server IP manzili

---

## QADAM 5 — nginx.conf sozlash

```bash
nano /opt/minimarket/nginx/conf.d/minimarket.conf
```

`YOUR_DOMAIN.COM` ni haqiqiy domeningiz bilan almashtiring.

**Agar domen yo'q bo'lsa (faqat IP):**
- SSL qismini o'chiring
- Faqat 80-port qolsin

---

## QADAM 6 — Deploy

```bash
cd /opt/minimarket
bash scripts/deploy.sh
```

---

## QADAM 7 — SSL (Ixtiyoriy, domen bo'lsa)

DNS sozlanganidan keyin (domen IP ga ko'rsatilgandan keyin):
```bash
bash scripts/ssl-setup.sh yourdomain.com sizning@email.com
docker compose -f docker-compose.prod.yml restart nginx
```

---

## Foydali buyruqlar

```bash
# Loglarni ko'rish
docker compose -f docker-compose.prod.yml logs -f

# Faqat backend logi
docker compose -f docker-compose.prod.yml logs -f backend

# Container holati
docker compose -f docker-compose.prod.yml ps

# Django superuser yaratish
docker compose -f docker-compose.prod.yml exec backend \
    python manage.py createsuperuser

# Ma'lumotlar bazasi backup
docker compose -f docker-compose.prod.yml exec db \
    pg_dump -U minimarket_user minimarket_db > backup.sql

# Restart
docker compose -f docker-compose.prod.yml restart

# To'xtatish
docker compose -f docker-compose.prod.yml down
```

---

## Muammolar

| Muammo | Yechim |
|--------|--------|
| Frontend yuklanmaydi | `next.config.ts` da `output: "standalone"` bormi? |
| API 404 | nginx.conf dagi `/api/` yo'naltirish to'g'rimi? |
| DB ulanmaydi | `.env.production` dagi `DATABASE_URL` da `db` host bo'lishi kerak |
| Celery ishlamaydi | Redis URL `redis://redis:6379/0` (docker network nomi) |
