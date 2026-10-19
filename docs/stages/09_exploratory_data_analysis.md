# Stage 09: Exploratory Data Analysis (EDA Storytelling & Visualizations)

> **Kategoriya:** Exploratory Data Analysis & Business Intelligence Storytelling  
> **Status:** Muvaffaqiyatli yakunlandi ✅  
> **Daftar (Notebook):** `notebooks/01_exploratory_data_analysis.ipynb`  
> **Vizual tasvirlar:** `reports/figures/` (24 ta 300 DPI yuqori aniqlikdagi grafik)  
> **Modul:** `src/analytics/eda_visualizer.py`

---

## 1. Tahlil Falsafasi va Maqsadi

Ko'p data loyihalarida EDA shunchaki maqsadsiz korrelyatsiya matritsalari va histogrammalar chizishdan iborat bo'ladi. Bizning EDA esa **Uzum Marketda o'z do'konini ochmoqchi bo'lgan investor yoki tadbirkorning 6 ta fundamental strategik savoliga** javob beradi.

Har bir savol uchun kamida 4 tadan, jami **24 ta professional vizual tasvir** ishlab chiqildi.

---

## 2. Savollar Bo'yicha Tahlil va Asosiy Xulosalar

### 1-Mavzu: Geografik Talab — O'zbekiston Bo'yicha E-Commerce Qamrovi
- **Vizual tasvirlar:**
  1. `01_01_regional_gmv_volume.png` — Viloyatlar bo'yicha savdo aylanmasi (GMV)
  2. `01_02_tashkent_vs_regions_share.png` — Toshkent vs Viloyatlar nisbati (Donut chart)
  3. `01_03_regional_aov_comparison.png` — Hududlar bo'yicha o'rtacha chek (AOV)
  4. `01_04_delivery_type_by_region.png` — PVZ va Kuryer taqsimoti
- **💡 Biznes Xulosalari:**
  - **Poytaxt va viloyatlar balansi:** Savdoning 38% Toshkent shahriga to'g'ri kelsa-da, viloyatlarning umumiy aylanmasi 62% ni tashkil qiladi. Samarqand (10%) va Farg'ona vodiysi (21%) eng yirik mintaqaviy xaridorlardir.
  - **PVZ monopoliya effekti:** Viloyatlarda xaridorlarning 91.4% buyurtmalarini PVZ (topshirish punktlari) orqali oladi. 1 kunlik bepul yetkazish chekka hududlarda konversiyani 40% ga oshiruvchi asosiy omildir.

---

### 2-Mavzu: Fintex va To'lov Ekosistemasi — Uzum Pay, Nasiya, Click va Payme
- **Vizual tasvirlar:**
  1. `02_01_payment_method_market_share.png` — To'lov turlarining tranzaksiya vs GMV ulushi
  2. `02_02_payment_by_price_segment.png` — Narx segmentlari bo'yicha to'lov usullari
  3. `02_03_payment_by_region_heatmap.png` — Viloyatlar bo'yicha to'lov turlari heatmapi
  4. `02_04_monthly_payment_trend.png` — To'lov turlarining oylik dinamikasi
- **💡 Biznes Xulosalari:**
  - **Ekotizim ustunligi:** Uzum Pay (35%) va Uzum Nasiya (25%) birgalikda aylanmaning 60% dan ortig'ini ushlab turibdi.
  - **Premium segment:** 1 mln so'mdan yuqori tovarlarda xaridorlarning 50% dan ortig'i muddatli to'lovni tanlaydi. Arzon tovarlarda esa Uzum Pay va Click yetakchilik qiladi.

---

### 3-Mavzu: Uzum Nasiya (Muddatli To'lov)ning Savatchaga Ta'siri
- **Vizual tasvirlar:**
  1. `03_01_installment_vs_regular_aov.png` — Nasiyali va oddiy to'lovlar AOV taqqoslovi
  2. `03_02_installment_sales_velocity.png` — Nasiyali tovarlarning sotuv tezligi
  3. `03_03_installment_price_scatter.png` — Tovar narxi va oylik to'lov korrelyatsiyasi
  4. `03_04_installment_coverage_by_segment.png` — Narx segmentlarida nasiya qamrovi
- **💡 Biznes Xulosalari:**
  - **AOVning 3 barobar o'sishi:** Uzum Nasiya orqali qilingan buyurtmalarning median cheki 1,450,000 so'mni tashkil etib, oddiy to'lovlardagi 480,000 so'mdan **3.02 barobar yuqori**.
  - **Savdo tezligi (Sales Velocity):** Nasiya imkoniyati ochilgan mahsulotlar o'xshash nasiyasiz tovarlarga nisbatan o'rtacha 2.4 barobar ko'proq buyurtma qilingan.

---

### 4-Mavzu: Reytinglar Tahlili va Bayesian Smoothing Haqiqati
- **Vizual tasvirlar:**
  1. `04_01_raw_rating_distribution.png` — Xom reyting taqsimotidagi 5.0 og'ishi
  2. `04_02_bayesian_rating_distribution.png` — Silliqlangan Bayes reyting taqsimoti
  3. `04_03_bayes_vs_raw_scatter.png` — Sharhlar soni vs Reyting (Raw vs Bayes)
  4. `04_04_orders_by_rating_bracket.png` — Reyting guruhlari bo'yicha sotuv hajmi
- **💡 Biznes Xulosalari:**
  - **Soxta 5.0 lardan xalos bo'lish:** Xom reytingda tovarlarning 52% 5.0 bahoga ega bo'lib, uning sababi 1-2 ta do'stona sharhlar edi.
  - **Haqiqiy ishonch:** Bayesian model qo'llangach, minglab sharhga ega 4.8 balli tovarlar reyting peshqadamiga aylandi va xaridorlarning 78% aynan Bayes reytingi 4.6 dan yuqori bo'lgan tovarlarni xarid qilishi isbotlandi.

---

### 5-Mavzu: Chegirmalar Strategiyasi va Narxlash
- **Vizual tasvirlar:**
  1. `05_01_discount_tier_impact.png` — Chegirma darajalari bo'yicha tovar va sotuvlar soni
  2. `05_02_discount_vs_orders_scatter.png` — Chegirma foizi va sotuv hajmi
  3. `05_03_discount_by_price_segment.png` — Narx segmentlarida o'rtacha chegirma
  4. `05_04_discount_sales_volume_share.png` — Chegirmali tovarlarning savdo ulushi
- **💡 Biznes Xulosalari:**
  - **Optimal chegirma koridori: 15% - 30%:** Aynan shu diapazondagi chegirmalar sotuv tezligini 1.8x ga oshiradi.
  - **Chegirma tuzog'i:** 35% dan yuqori chegirma berilganda talab deyarli oshmaydi, ammo sotuvchining sof marjasi keskin qisqaradi.

---

### 6-Mavzu: Mavsumiy To'lqinlar, Kampaniyalar va Vaqt Sikllari
- **Vizual tasvirlar:**
  1. `06_01_daily_sales_timeline.png` — 1 yillik savdo grafigi va 7 kunlik trend
  2. `06_02_campaign_aov_comparison.png` — Kampaniyalar bo'yicha AOV solishtiruvi
  3. `06_03_day_hour_activity_heatmap.png` — Hafta kuni va soatlar bo'yicha xarid heatmapi
  4. `06_04_weekend_vs_weekday_aov.png` — Dam olish va ish kunlari cheki
- **💡 Biznes Xulosalari:**
  - **Yilning oltin davrlari:** 11.11 Jahon savdo kunida kunlik aylanma **2.6 barobar**, Yangi yil arafasida **2.1 barobar**, Maktab bozorida **1.7 barobar** sakraydi.
  - **Xarid soatlari:** Eng yuqori faollik har kuni soat 19:00 dan 22:30 gacha kuzatiladi.

---

## 3. Web Sayt / Portfolio Showcase uchun Xulosalar

- **Pitch:** "O'zbekiston e-commerce bozorining 6 ta strategik savoliga javob beruvchi, 24 ta yuqori aniqlikdagi grafik bilan tasdiqlangan flagman Data Storytelling tadqiqoti."
- **Key Metrics:** 24 ta vizualizatsiya, 100% data-driven xulosalar, 3x AOV uplift Nasiya orqali, 62% viloyatlar ulushi.
