# 🍇 Uzum Market: End-to-End Data Science & Business Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-In%20Development-yellow.svg)]()
[![Code%20Style](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

O'zbekistondagi eng yirik e-commerce ekotizimi bo'lgan **Uzum Market** ma'lumotlarini chuqur Data Analytics, Machine Learning va Business Intelligence nuqtai nazaridan tahlil qilishga mo'ljallangan ishlab chiqarish (production) darajasidagi data science loyihasi.

---

## 📌 Loyiha Arxitekturasi

Ushbu loyiha **Cookiecutter Data Science** xalqaro sanoat standarti asosida modulli arxitekturada qurilgan:

```text
uzum_project/
├── config/                  # Markaziy konfiguratsiyalar (config.yaml)
├── data/                    # Ma'lumotlar ombori
│   ├── raw/                 # Xom ma'lumotlar (hech qachon o'zgartirilmaydi)
│   └── processed/           # Tozalangan va tahlilga tayyor ma'lumotlar
├── notebooks/               # Tartiblangan tadqiqot daftarlari (EDA, Stats)
├── reports/                 # Hisobotlar va vizualizatsiyalar
│   └── figures/             # Yuqori aniqlikdagi grafiklar
├── src/                     # Ishlab chiqarish modullari
│   ├── data_collection/     # Asinxron skreper va ma'lumot yig'ish vositalari
│   ├── processing/          # Ma'lumotlarni tozalash va Feature Engineering
│   ├── analytics/           # Biznes, mijoz (RFM) va narx elastikligi modullari
│   ├── models/              # ML modellari, forecasting va tavsiya tizimlari
│   └── dashboard/           # Streamlit interaktiv boshqaruv paneli
├── tests/                   # Data validation va unit testlar
├── .gitignore               # Xavfsizlik va repository gigiyenasi
├── pyproject.toml           # Qaramliklar va loyiha konfiguratsiyasi
└── README.md                # Asosiy hujjatlashtirish
```

---

## 🚀 Quick Start (Tezkor Ishga Tushirish)

### 1. Virtual muhitni yaratish va faollashtirish
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
```

### 2. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

---

## 🧭 Yo'l Xaritasi (Roadmap)
Loyihaning to'liq 25 bosqichli professional rejasi bilan tanishish uchun yo'l xaritasini ko'ring.
