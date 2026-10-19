# Stage 03: Data Collection Strategy & Ingestion Engine

> **Kategoriya:** Data Ingestion & Synthetic Simulation  
> **Status:** Muvaffaqiyatli yakunlandi ✅  
> **Modullar:** `src/data_collection/scraper.py`, `src/data_collection/order_generator.py`  
> **Hosil bo'lgan artefaktlar:** `data/raw/uzum_catalog_raw.json` (1.51 MB), `data/raw/uzum_orders_raw.json` (7.6 MB)

---

## 1. Muammo va Muhandislik Yechimi

Ushbu bosqichda ikkita jiddiy sinovga duch keldik:
1. **Jonli ma'lumotlar manbasi:** Uzum Market zamonaviy Single Page Application (SPA) bo'lib, uning ichki GraphQL va API shlyuzlari maxsus himoyalangan. Biz platformaning ommaviy mobil oqimi (`https://api.uzum.uz/api/main/mobile`) orqali **real katalog** oqimini ochishga muvaffaq bo'ldik.
2. **Tranzaksiyalar maxfiyligi (Privacy barrier):** Hech bir e-commerce kompaniyasi xaridorlarning shaxsiy buyurtmalar tarixini ochiq e'lon qilmaydi. Shuning uchun haqiqiy skreper qilingan 2,260 ta tovar asosida O'zbekistonning demografik, moliyaviy va geografik xususiyatlarini aks ettiruvchi yuqori aniqlikdagi **tranzaksiyalar generatori**ni yaratdik.

---

## 2. Real Skreper Natijalari (`scraper.py`)

- **Bajarilish vaqti:** 4.91 soniya
- **Status:** HTTP 200 OK
- **Olingan tovarlar:** **2,260 ta unikal mahsulot**
- **Toifalar soni:** 363 ta takliflar va toifalar bloki
- **Qamrab olingan atributlar:** Haqiqiy sotuv narxi, asl narx, xaridorlar reytingi, sharhlar soni, tovar rasmlari va Uzum Nasiya oylik to'lov badgelari.

---

## 3. Tranzaksiyalar Tarixi Generatsiyasi (`order_generator.py`)

Haqiqiy tovarlarga bog'langan holda 1 yillik tranzaksiyalar modellashtirildi:
- **Jami buyurtmalar:** **16,917 ta buyurtma**
- **Jami mijozlar kohortasi:** **3,500 ta mijoz**
- **O'zbekiston bo'yicha taqsimot:**
  - Toshkent shahri: 38%
  - Toshkent viloyati: 12%
  - Samarqand: 10%
  - Farg'ona vodiysi (Farg'ona, Andijon, Namangan): 21%
  - Buxoro, Xorazm, Qashqadaryo, Surxondaryo, Navoiy, Jizzax, Qoraqalpog'iston: 19%
- **To'lov usullari taqsimoti:**
  - Uzum Pay: 35%
  - Uzum Nasiya (Muddatli to'lov): 25% (1 mln so'mdan yuqori tovarlarda 50% gacha)
  - Click: 20%
  - Payme: 12%
  - Naqd / Karta (PVZda): 8%
- **Mavsumiy to'lqinlar (Seasonality Spikes):** 11.11 Jahon savdo kuni (2.6x pik), Yangi yil (2.1x), Maktab bozori (1.7x), 8-mart va Navro'z (1.5x).

---

## 4. Web Sayt / Portfolio Showcase uchun Xulosalar

- **Pitch:** "Jonli Uzum Market API orqali 2,260 ta real tovar yig'ildi va 16,917 ta realistik savdo tranzaksiyasi bilan boyitildi."
- **Key Metrics:** 2,260 real SKU, 16,917 tranzaksiya, 13 ta hudud, 3,500 mijoz, 35% Uzum Pay / 25% Nasiya integratsiyasi.
