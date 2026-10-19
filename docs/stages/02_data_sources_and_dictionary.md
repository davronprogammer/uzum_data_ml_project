# Stage 02: Data Sources & Data Dictionary Specification

> **Kategoriya:** Data Governance & Domain Modeling  
> **Status:** Muvaffaqiyatli yakunlandi ✅  
> **Asosiy hujjat:** `docs/data_dictionary.md`

---

## 1. Muammo va Domen Tahlili

E-commerce tahlilida noto'g'ri tushunilgan bitta ustun (masalan, chegirmagacha bo'lgan narx bilan yakuniy narxni chalkashtirish yoki oylik muddatli to'lovni mahsulotning umumiy narxi deb hisoblash) butun moliya hisobotlarini yo'qqa chiqarishi mumkin.

O'zbekiston e-commerce bozorining (Uzum Market) o'ziga xos 2 ta asosiy lokomotiv omili mavjud:
1. **Uzum Nasiya (BNPL - Muddatli to'lov):** Savdo aylanmasining salmoqli qismi 3, 6, 12 oylik to'lovlar orqali amalga oshadi.
2. **Topshirish punktlari (PVZ) orqali 1 kunlik yetkazib berish:** Mijozlarning konversiya ko'rsatkichini belgilab beruvchi eng kuchli raqobat ustunligi.

---

## 2. Ishlab Chiqilgan Ma'lumotlar Lug'ati (Data Schema)

Biz 23 ta ustun bo'yicha qat'iy ma'lumotlar lug'atini (Data Contract) shakllantirdik:

- **Identifikatorlar va nomlar:** `product_id`, `title`, `category_id`, `category_name`, `category_path`, `seller_id`, `seller_name`
- **Narxlar va chegirmalar:** `price_current` (so'm), `price_original` (so'm), `discount_percentage`
- **Fintech & Muddatli to'lov:** `has_installment`, `monthly_installment` (so'm/oyiga), `installment_period_months`
- **Logistika & Yetkazish:** `delivery_time_days` (1 kun), `delivery_type` (PVZ / Courier)
- **Talab & Reyting ko'rsatkichlari:** `rating` (0..5), `reviews_count`, `orders_count`
- **Qo'shimcha atributlar:** `is_eco`, `is_adult`, `in_stock`, `crawled_at`

---

## 3. Data Integrity & Validatsiya Qoidalari

- `price_current > 0` va `price_original >= price_current`
- `discount_percentage ∈ [0.0, 100.0]`
- `rating ∈ [0.0, 5.0]`
- `orders_count >= 0` va `reviews_count >= 0`

---

## 4. Web Sayt / Portfolio Showcase uchun Xulosalar

- **Pitch:** "Loyiha doirasida O'zbekiston fintex va logistika xususiyatlarini (Uzum Nasiya va PVZ yetkazib berish) to'liq qamrab oluvchi 23 ustunli professional Data Dictionary standarti yaratildi."
- **Key Metrics:** 23 ta rasmiylashtirilgan analitik ustun, 100% tiplashtirilgan schema contract.
