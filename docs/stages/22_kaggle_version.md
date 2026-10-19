# 22-Bosqich: Kaggle Versiyasi va Ochiq Ma'lumotlar Ulashuvi (Open Data Release)

## Bosqich Maqsadi
Ushbu bosqichning maqsadi — tozalangan va boyitilgan O'zbekiston e-commerce ma'lumotlarini dunyo Data Science hamjamiyatining asosiy platformasi hisoblangan **Kaggle** uchun to'liq paketlash, rasmiy `dataset-metadata.json` metama'lumotlarini yaratish va Kaggle da e'tibor qozonuvchi mustaqil vizual storytelling notebook (`kaggle_uzum_showcase.ipynb`) ni taqdim etishdir.

---

## 1. Nima uchun kerakligi (Community & Portfolio Value)
Kaggle — butun dunyo bo'yicha 15+ milliondan ortiq data scientistlar, Machine Learning muhandislari va FAANG yollash menejerlari jamlangan eng yirik markazdir.
* **Markaziy Osiyo e-commerce ochiq datasi taqchilligi:** Global platformalarda (Amazon, Ozon, MercadoLibre) datasetlar juda ko'p, biroq O'zbekistonning tez rivojlanayotgan e-commerce (Uzum) bozori bo'yicha ma'lumotlar deyarli yo'q edi. Ushbu dataset mintaqa bo'yicha eng nufuzli benchmark manbasiga aylanadi.
* **Data Storytelling san'ati:** Kaggle'da yuqori medal (Gold/Silver) olish uchun shunchaki kod emas, balki aniq biznes savollar, grafiklar, gipotezalar va tavsiyalar uyg'unligi talab qilinadi.

---

## 2. Amalga oshirilgan ishlar va Deliverables

1. **Kaggle To'plami (`data/kaggle/`):**
   - `products.csv`: 2,260 ta tovar, narxlar, reytinglar va nasiya badjlari.
   - `orders.csv`: 16,917 ta buyurtma, to'lov usullari, yetkazish hududlari.
   - `order_items.csv`: Savatdagi tovar birliklari.
   - `customers.csv`: 3,500 ta mijoz profillari.
   - `categories.csv`: Ierarxik kategoriya daraxti.
   - `customer_rfm_segments.csv`: 11 ta mijozlar xulq-atvor segmenti.
   - `price_elasticity_by_category.csv`: Narx elastikligi (PED) koeffitsientlari.
   - `product_abc_xyz_analysis.csv`: ABC/XYZ assortiment matritsasi.
   - `sales_forecast_60d.csv`: 60 kunlik talab prognozi.
2. **Kaggle Metadata (`data/kaggle/dataset-metadata.json`):**
   - CC0-1.0 (Public Domain) litsenziyasi.
   - Kalit so'zlar: `ecommerce`, `retail`, `uzbekistan`, `rfm-segmentation`, `demand-forecasting`.
   - Har bir fayl uchun batafsil tavsiflar.
3. **Kaggle Storytelling Notebook (`notebooks/kaggle_uzum_showcase.ipynb`):**
   - Hech qanday tashqi fayllarga bog'liq bo'lmagan, to'liq mustaqil (Self-contained) Jupyter Notebook.
   - 7 ta bo'lim: Ma'lumotlarni yuklash, moliyaviy KPIlar, regional logistika tahlili, Uzum Nasiya AOV effekti (Welch t-test), RFM segmentlari, 60 kunlik prognoz va biznes tavsiyalar.
4. **Sifat Testlari (`tests/test_kaggle_package.py`):**
   - 3 ta unit-test metadata to'g'riligi, CSV fayllar satrlar soni va notebook JSON formatini 100% muvaffaqiyatli tekshirdi.

---

## 3. Kaggle Platformasiga Yuklash Qo'llanmasi
```bash
# 1. Kaggle CLI orqali yuklash:
pip install kaggle

# 2. dataset-metadata.json ichidagi "id" ni o'z usernameingizga moslang:
# "id": "username/uzum-market-ecommerce-dataset"

# 3. Buyruqni ishga tushiring:
kaggle datasets create -p data/kaggle/
```
