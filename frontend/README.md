# Mini Market POS — Frontend

Next.js 15 + TypeScript + Tailwind CSS + Zustand + React Query

## Tez boshlash

```bash
cp .env.example .env.local
# .env.local ni o'zgartiring

npm install
npm run dev
# http://localhost:3000
```

## Stack

| Kutubxona | Maqsad |
|-----------|--------|
| Next.js 15 | App Router, SSR |
| TypeScript | Type safety |
| Tailwind CSS | Styling |
| Zustand | Global state (auth, cart) |
| TanStack Query | Server state, caching |
| Axios | HTTP + interceptors |
| React Hook Form + Zod | Form validation |
| next-themes | Dark/Light mode |
| Recharts | Grafiklar |
| @zxing/browser | Kamera barcode scanner |
| react-hot-toast | Notifications |
| lucide-react | Ikonkalar |

## Sahifalar

| Sahifa | URL | Tavsif |
|--------|-----|--------|
| Login | `/login` | JWT auth |
| Dashboard | `/` | Statistika, grafik |
| POS/Kassa | `/pos` | Cart + barcode + to'lov |
| Mahsulotlar | `/products` | CRUD |
| Xaridlar | `/purchases` | Company → Purchase |
| Ombor | `/inventory` | Qoldiqlar |
| Kompaniyalar | `/companies` | Company + Branch |
| Sotuvlar | `/sales` | Tarix |
| Hisobotlar | `/reports` | PDF/Excel |
| Tarix | `/history` | AuditLog |
| Sozlamalar | `/settings` | Profil, parol, til |

## Til qo'shish

`src/i18n/` papkasiga yangi JSON fayl qo'shing,
`src/i18n/index.ts` da `translations` ga qo'shing.
