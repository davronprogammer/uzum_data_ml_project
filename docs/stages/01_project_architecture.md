# Stage 01: Project Architecture & Environment Setup

> **Kategoriya:** MLOps & Analytics Engineering  
> **Status:** Muvaffaqiyatli yakunlandi ✅  
> **Arxitektura standarti:** Cookiecutter Data Science (Production-Ready)

---

## 1. Muammo va Arxitektura Qarori

Katta hajmdagi Data Science va Business Intelligence loyihalarida eng ko'p uchraydigan xato — barcha kodlarni bitta tartibsiz Jupyter Notebook yoki yagona skriptga to'plashdir. Bu loyihani qayta takrorlanuvchan (reproducible) bo'lmasligiga, versiyalash qiyinlashishiga va jamoaviy hamkorlikning barbod bo'lishiga olib keladi.

Biz ushbu muammoni hal qilish uchun **Cookiecutter Data Science** xalqaro sanoat andozasi asosida qat'iy modulli arxitektura barpo etdik.

---

## 2. Ishlab Chiqilgan Komponentlar va Struktura

```text
uzum_project/
├── config/                  # Markaziy parametrlar (config.yaml)
├── data/                    # Ma'lumotlar ombori
│   ├── raw/                 # Xom ma'lumotlar (hech qachon tahrirlanmaydi)
│   └── processed/           # Tozalangan va tahlilga tayyor ma'lumotlar
├── docs/                    # Loyiha hujjatlari va texnik spesifikatsiyalar
│   └── stages/              # Har bir bosqichning batafsil hisoboti
├── notebooks/               # Tartiblangan tadqiqot daftarlari
├── reports/                 # Hisobotlar va vizualizatsiyalar
│   └── figures/             # Yuqori aniqlikdagi grafiklar
├── src/                     # Ishlab chiqarish modullari
│   ├── data_collection/     # Skreper va ingestion vositalari
│   ├── database/            # Baza sxemalari va DDL
│   ├── processing/          # ETL va Feature Engineering
│   ├── analytics/           # Biznes, mijoz va savdo tahlili
│   ├── models/              # ML modellari, forecasting va recsys
│   └── dashboard/           # Streamlit BI boshqaruv paneli
├── tests/                   # Data validation va sifat testlari
├── .gitignore               # Xavfsizlik va repository gigiyenasi
├── requirements.txt         # Loyiha qaramliklari
└── README.md                # Repozitoriy portret hujjati
```

---

## 3. Foydalanilgan Texnologiyalar va Sabablari

| Asbob / Texnologiya | Roli | Nima uchun tanlandi? |
| :--- | :--- | :--- |
| **Python 3.11+** | Asosiy dasturlash tili | Zamonaviy tezkor sintaksis va kutubxonalar ekotizimi |
| **Git & Conventional Commits** | Versiyalarni boshqarish | Commit tarixini xalqaro kompaniyalar standartiga keltirish |
| **YAML (`config.yaml`)** | Konfiguratsiya boshqaruvi | Qattiq kodlangan (hardcoded) yo'l va o'zgaruvchilardan to'liq xalos bo'lish |
| **Ruff & Flake8** | Kod sifati va linter | PEP 8 standartlariga rioya etish |

---

## 4. Xavfsizlik va Git Gigiyenasi (`.gitignore`)

- Gigabaytlab xom ma'lumotlar va model og'irliklari (`*.pkl`, `*.parquet`) repozitoriyga tasodifan yuklanishining oldi olindi.
- Maxfiy kalitlar (`.env`, `secrets/`) to'liq himoyalandi.
- Bo'sh kataloglar strukturasi Git'da saqlanib qolishi uchun har biriga `.gitkeep` joylashtirildi.

---

## 5. Web Sayt / Portfolio Showcase uchun Xulosalar

- **Pitch:** "Ushbu loyiha shunchaki tahliliy notebook emas, balki korporativ darajadagi modulli Python paketlar tizimi sifatida loyihalashtirilgan."
- **Key Metrics:** 11 ta maxsus katalog, to'liq izolyatsiya qilingan muhit, 100% Conventional Commits intizomi.
