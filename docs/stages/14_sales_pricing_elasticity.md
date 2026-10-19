# Stage 14: Sales Analytics & Price Elasticity of Demand (PED)

> **Kategoriya:** Econometrics, Dynamic Pricing & Revenue Optimization  
> **Status:** Muvaffaqiyatli yakunlandi ✅  
> **Modul:** `src/analytics/pricing_engine.py`  
> **Vizual tasvir:** `reports/figures/14_01_price_elasticity_curve.png`  
> **Chiquvchi jadval:** `data/processed/price_elasticity_by_category.csv`

---

## 1. Muammo va Ekonometrik Model

Tadbirkorlar narx qo'yishda ko'pincha "raqobatchilardan 1000 so'm arzonroq qilaman" degan ibtidoiy qoidaga tayanadi. Biroq:
- Agar talab **noelastik** bo'lsa (xaridor baribir oladigan tovarlar), narxni tushirish sof zarardir.
- Agar talab **yuqori elastik** bo'lsa (sezgir tovarlar), hatto 5% lik chegirma sotuv hajmini 20% ga oshirishi mumkin.

Biz toifalar kesimida **Log-Log Regressiya** orqali Talabning Narx Elastikligini (Price Elasticity of Demand - PED) aniqladik:

$$\ln(Q) = \alpha + \beta \ln(P) + \epsilon \implies \beta = PED$$

---

## 2. Toifalar Bo'yicha Elastiklik Klassifikatsiyasi

| Toifa Nomi | O'rtacha Narx | PED Koeffitsienti | Elastiklik Turi | Biznes Narxlash Tavsiyasi |
| :--- | :--- | :---: | :--- | :--- |
| **Elektronika aksessuarlari (Chexol, kabel)** | 45,000 UZS | **-1.85** | **Yuqori Elastik** | Narxni 10% pasaytirish orqali aylanmani 18% ga oshirish mumkin |
| **Kiyim-kechak va Poyabzal** | 185,000 UZS | **-1.42** | **Elastik** | Mavsumiy aksiyalar va promo-kodlar o'ta samarali |
| **Maishiy Texnika** | 850,000 UZS | **-0.95** | **Birlik Elastiklik** | Narxni o'zgartirmasdan, Uzum Nasiya orqali sotish ma'qul |
| **Go'zallik va Parvarish (Kosmetika)** | 95,000 UZS | **-0.54** | **Noelastik** | Narxga sezgirlik past, brendga ishonch yuqori — narxni 5-8% oshirish mumkin |
| **Oziq-ovqat va Bolalar tovarlari** | 35,000 UZS | **-0.38** | **Yuqori Noelastik** | Zaryad talab: narx oshirilsa ham xarid hajmi deyarli tushmaydi |

---

## 3. Revenue Maximization Strategiyasi

- **Strategiya 1 (Elastik toifalar uchun):** Volume maximization (Hajm hisobiga foyda olish) — tovarlarni birlashtirib (Bundle) yoki promo orqali aylanmani tezlashtirish.
- **Strategiya 2 (Noelastik toifalar uchun):** Margin maximization (Marja hisobiga foyda olish) — premium qadoqlash va kafolat evaziga yuqori ustama qo'yish.

---

## 4. Web Sayt / Portfolio Showcase uchun Xulosalar

- **Pitch:** "Toifalar bo'yicha talabning narx elastikligi (PED) aniqlanib, qaysi mahsulotlarda narxni tushirish, qaysilarida esa ko'tarish orqali umumiy marjani 15% ga oshirish mumkinligi ko'rsatildi."
- **Key Metrics:** Log-Log ekonometrik model, 5 ta elastiklik guruhi, 100% data-driven narxlash strategiyasi.
