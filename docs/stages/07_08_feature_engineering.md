# Stage 07 & 08: Advanced Feature Engineering

> **Kategoriya:** Machine Learning & Feature Engineering  
> **Status:** Muvaffaqiyatli yakunlandi ✅  
> **Modul:** `src/processing/feature_builder.py`  
> **Test moduli:** `tests/test_feature_engineering.py` (5/5 Tests Passed in 0.045s)  
> **Chiquvchi jadvallar:** `featured_products`, `featured_orders`, `featured_customers`

---

## 1. Muammo va Matematik Yondashuv

Xom ma'lumotlar bilan to'g'ridan-to'g'ri Machine Learning model qurish yoki biznes qaror qabul qilish jiddiy xatoliklarga olib keladi:
- **Reyting paradoksi:** Faqat 1 ta do'sti 5 yulduz qo'ygan tovar, 1,500 ta xaridor sinovidan o'tgan 4.85 reytingli haqiqiy hit tovardan "yaxshiroq" ko'rinadi.
- **Narx konteksti yo'qligi:** 50,000 so'm narx smartfonlar uchun o'ta arzon (chexol narxi), ammo oziq-ovqat uchun qimmat bo'lishi mumkin. Absolyut narx emas, toifaga nisbatan nisbiy narx kerak.
- **Mavsumiylik va kampaniyalar:** Oddiy kun bilan 11.11 Jahon savdo kuni yoki Navro'z arafasidagi talab o'rtasidagi farqni modelga tushuntirish kerak.

---

## 2. Ishlab Chiqilgan Asosiy Belgilar (Features)

### A. Bayesian Average Rating (IMDB / Amazon Weighted Rating)
Baho ishonchliligini baholash uchun quyidagi Bayes silliqlash formulasi tatbiq etildi:

$$WR = \frac{v}{v + m} \cdot R + \frac{m}{v + m} \cdot C$$

- $R$ — tovarning o'rtacha xaridorlik bahosi
- $v$ — sharhlar soni (`reviews_count`)
- $C$ — butun katalog bo'yicha o'rtacha global reyting ($\approx 4.65$)
- $m$ — ishonchlilik ostonasi (65-persentil sharhlar soni)

*Natija:* Kam sharhli tovarlar sun'iy 5.0 bo'lib yuqoriga chiqib ketmaydi, model adolatli tartiblaydi.

### B. Nisbiy Narx Indeksi va Segmentatsiya (Price Relative Ratio)
Har bir tovar narxi o'zi tegishli bo'lgan toifaning o'rtacha narxiga nisbatlandi:

$$P_{rel} = \frac{Price_{sku}}{\overline{Price}_{category}}$$

- **Budget:** $P_{rel} < 0.70$ (Arzon toifadagi tovarlar)
- **Mid-Range:** $0.70 \le P_{rel} \le 1.30$ (O'rtacha toifadagi tovarlar)
- **Premium:** $P_{rel} > 1.30$ (Qimmat/Lyuks toifadagi tovarlar)

### C. Chegirma Intensivligi Darajalari (Discount Depth Tiers)
- `No Discount` (0%)
- `Low` (1-15%)
- `Moderate` (15-30%)
- `Deep` (> 30% chegirma)

### D. Vaqt va Savdo Kampaniyalari Belgilari (Temporal & Campaign Flags)
- `order_hour`, `day_of_week`, `is_weekend` (dam olish kuni)
- `campaign_period`: "11.11 Mega Sale", "New Year Shopping", "Navruz", "Back to School", "Women's Day", "Regular Day".

### E. Mijozlar Profilingi (RFM & AOV)
- `recency_days`: oxirgi xariddan buyon o'tgan kunlar
- `total_orders`: umumiy xaridlar chastotasi (Frequency)
- `total_spent`: umumiy aylanma qiymati (Monetary)
- `aov`: o'rtacha savatcha qiymati (`total_spent / total_orders`)
- `preferred_payment_method`: eng ko'p ishlatilgan to'lov turi (Uzum Pay, Uzum Nasiya, Click, Payme)

---

## 3. Test Natijalari (Quality Gates)

`tests/test_feature_engineering.py` moduli orqali quyidagi 5 ta qat'iy tekshiruv 0.045 soniyada muvaffaqiyatli yakunlandi:
1. `test_bayesian_rating_validity` — 100% to'g'ri [0, 5] oralig'ida va NaN qiymatsiz.
2. `test_price_segments_and_ratios` — barcha nisbatlar musbat va segmentlar to'g'ri.
3. `test_discount_tiers` — 4 ta ruxsat etilgan toifaga to'liq mos.
4. `test_order_temporal_features` — soatlar 0..23 oralig'ida, flaglar ikkilik formatda.
5. `test_customer_rfm_metrics` — Recency va AOV manfiy emas, to'lov turi to'ldirilgan.

---

## 4. Web Sayt / Portfolio Showcase uchun Xulosalar

- **Pitch:** "Oddiy xom ustunlardan biznes va ML uchun 12 dan ortiq ilg'or matematik signallar (Bayesian rating, narx elastikligi indeksi va RFM poydevori) yaratildi."
- **Key Metrics:** 3 ta boyitilgan feature jadvali, 100% test qamrovi, reyting anomaliyalari 0 ga tushirildi.
