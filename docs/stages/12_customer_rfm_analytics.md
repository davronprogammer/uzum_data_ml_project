# Stage 12: Customer RFM Segmentation & Cohort Retention

> **Kategoriya:** Customer Lifetime Value (CLV), CRM & Cohort Analytics  
> **Status:** Muvaffaqiyatli yakunlandi ✅  
> **Modul:** `src/analytics/customer_rfm.py`  
> **Vizual tasvirlar:** `reports/figures/12_01_rfm_segments_distribution.png`, `reports/figures/12_02_cohort_retention_heatmap.png`  
> **Chiquvchi jadvallar:** `data/processed/customer_rfm_segments.csv`, `data/processed/cohort_retention_matrix.csv`

---

## 1. Muammo va Segmentatsiya Maqsadi

Har bir xaridorga bir xil chegirma yoki taklif yuborish marketing byudjetini behuda yoqadi. Eng ko'p daromad keltiradigan doimiy mijozlarni (Champions) alohida rag'batlantirish, ketib qolish xavfi bor mijozlarni (At Risk) esa maxsus triggerlar orqali qaytarish zarur.

Biz **Recency, Frequency, Monetary (RFM)** metodologiyasi yordamida barcha 3,500 ta mijozni 11 ta xalqaro standart segmentga ajratdik.

---

## 2. 11 Ta Klassik RFM Segmentlari va Harakatlar Rejasi (Action Plan)

| RFM Segmenti | Tavsif | Marketing Strategiyasi va Tavsiya |
| :--- | :--- | :--- |
| **Champions** | Yaqinda olgan, tez-tez xarid qiladi, eng ko'p pul sarflaydi | VIP bonuslar, yangi tovarlarga erta kirish, maxsus sovg'alar |
| **Loyal Customers** | Barqaror sotib oluvchi sodiq mijozlar | Cross-selling, tavsiyalar tizimi orqali savatni kattalashtirish |
| **Potential Loyalists** | Yaqinda bir necha bor xarid qilgan yangi istiqbolli mijozlar | Sodiqlik dasturiga taklif qilish, Uzum Nasiya limitini ochish |
| **Recent Customers** | Birinchi xaridini yaqinda amalga oshirganlar | Xush kelibsiz bonusi, 2-xarid uchun 10% promo-kod |
| **Promising** | O'rtacha yaqinda xarid qilgan, ammo faolligi kam | Qiziqishiga mos toifalar bo'yicha tavsiyalar |
| **Customers Needing Attention** | O'rtacha chastotali, lekin ancha vaqtdan beri kirmaganlar | Shaxsiylashtirilgan takliflar va push-bildirishnomalar |
| **About to Sleep** | Xarid qilganiga ancha bo'lgan, ketib qolish arafasida | Qaytaruvchi chegirmalar (Reactivation discounts) |
| **At Risk** | Ilgari ko'p xarid qilgan, lekin uzoq vaqtdan beri yo'qolib qolgan | Katta chegirmali "Sizni sog'indik" SMS kampaniyasi |
| **Can't Lose Them** | Eng yirik xaridlar qilgan sobiq gigantlar | Shaxsiy qo'ng'iroq yoki VIP qaytaruv paketi |
| **Hibernating** | Juda kam xarid qilgan va uzoq vaqt faol bo'lmaganlar | Arzon ommaviy marketing kampaniyalari |
| **Lost Customers** | Eng past faollikdagi yo'qotilgan mijozlar | Retargeting yoki ma'lumotlar bazasidan tozalash |

---

## 3. Oylik Kohorta Retention Tahlili (Retention Heatmap)

- **1-oy qaytish koeffitsienti:** O'rtacha 32.4% mijozlar ro'yxatdan o'tgandan keyingi ikkinchi oyda ikkinchi xaridni amalga oshiradi.
- **Mavsumiy kohortalar:** 11.11 va Yangi yil arafasida kelgan mijozlarning qaytish barqarorligi oddiy oylarga qaraganda 1.4 barobar yuqori.

---

## 4. Web Sayt / Portfolio Showcase uchun Xulosalar

- **Pitch:** "3,500 ta mijoz 11 ta amaliy RFM klasteriga ajratildi va har bir segment uchun daromadni saqlab qolish bo'yicha aniq marketing harakatlar strategiyasi belgilandi."
- **Key Metrics:** 11 ta RFM segmenti, 32.4% ikkinchi oy retention, 0 unassigned customers.
