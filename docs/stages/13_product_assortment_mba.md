# Stage 13: Product Assortment (ABC/XYZ) & Market Basket Analysis (MBA)

> **Kategoriya:** Inventory Optimization & Cross-Selling Analytics  
> **Status:** Muvaffaqiyatli yakunlandi ✅  
> **Modul:** `src/analytics/product_analytics.py`  
> **Vizual tasvirlar:** `reports/figures/13_01_abc_xyz_matrix_heatmap.png`, `reports/figures/13_02_market_basket_top_rules.png`  
> **Chiquvchi jadvallar:** `data/processed/product_abc_xyz_analysis.csv`, `data/processed/market_basket_rules.csv`

---

## 1. Muammo va Zaxirani Boshqarish (Inventory Management)

Uzum Marketda do'kon yurituvchi tadbirkorning eng katta xatosi — aylanmaydigan tovarlarga pul tikib, aylanma mablag'ni muzlatib qo'yishdir (Deadstock). Shu bilan birga, eng ko'p talab bor tovarlar omborda tugab qolsa (Stockout), savdo yo'qotiladi.

Biz bu muammoni **ABC/XYZ Assortiment Matritsasi** va **Market Basket Analysis (Apriori qoidalari)** orqali yechdik.

---

## 2. ABC/XYZ 9-Segmentli Assortiment Matritsasi

- **ABC Tahlili (Aylanma ulushi):**
  - **A (80% aylanma):** Eng lokomotiv tovarlar (katalogning ~15-20% qismi)
  - **B (15% aylanma):** O'rtacha barqaror tovarlar (~30%)
  - **C (5% aylanma):** Kam aylanadigan tovarlar (~50%)
- **XYZ Tahlili (Talab noaniqlik koeffitsienti CV):**
  - **X (CV <= 0.15):** Doimiy va rejalashtirish oson bo'lgan talab
  - **Y (0.15 < CV <= 0.35):** Mavsumiy yoki o'zgaruvchan talab
  - **Z (CV > 0.35):** Kutilmagan, beqaror talab

### 9 Segment Bo'yicha Boshqaruv Qoidalari:
1. **AX toifasi:** Oltin zaxira — omborda 1 kun ham tugamasligi shart (Avtomatik to'ldirish).
2. **AY toifasi:** Mavsum oldidan katta hajmda zaxiralanadi (Navro'z, Maktab bozori, Yangi yil).
3. **AZ toifasi:** Yuqori tushumli, ammo xavfli tovarlar — faqat aniq talab bashorati asosida olib kelinadi.
4. **CZ toifasi:** Likvidatsiya qilish kerak bo'lgan xavfli "o'lik yuk" — darhol chegirma bilan sotib yuborish lozim.

---

## 3. Market Basket Analysis (Savatcha Assotsiativ Qoidalari)

Mijozlar savatchasidagi tovarlar tahlili orqali Cross-Selling (birga sotish) qoidalari topildi:
- **Support:** $P(A \cap B)$ — ikkala tovarning birga uchrash chastotasi
- **Confidence:** $P(B | A)$ — A olinganda B ham olinishi ehtimoli
- **Lift:** $Lift > 1.0$ bo'lsa, tovarlar tasodifdan ko'ra ko'proq birga olinayotganini bildiradi.

*Amaliy misol:* Smartfon xarid qilinganda, himoya oynasi va chexolning savatga tushish ehtimoli oddiy tovarlarga qaraganda **3.4 barobar yuqori (Lift = 3.42)**.

---

## 4. Web Sayt / Portfolio Showcase uchun Xulosalar

- **Pitch:** "2,260 ta tovar 9 ta ABC/XYZ zaxira klasteriga ajratildi va savat kattaligini oshiruvchi Lift > 2.5 bo'lgan top Cross-Selling qoidalari ishlab chiqildi."
- **Key Metrics:** 9 ta inventar segmenti, top assotsiativ qoidalar, o'lik zaxiralarni 40% ga qisqartirish tavsiyalari.
