# Stage 16: Multi-Model Demand Forecasting & Backtesting

> **Kategoriya:** Machine Learning Time Series Forecasting  
> **Status:** Muvaffaqiyatli yakunlandi ✅  
> **Modul:** `src/models/forecasting.py`  
> **Test moduli:** `tests/test_forecasting.py` (2/2 Tests Passed in 2.04s)  
> **Vizual tasvir:** `reports/figures/16_01_sales_forecast_comparison.png`  
> **Chiquvchi jadval:** `data/processed/sales_forecast_60d.csv`

---

## 1. Muammo va Muhandislik Arxitekturasi

E-commerce'da aniq talab prognozi (Demand Forecasting) bo'lmasa, do'kon egasi ikki muammoga uchraydi:
1. **Stockout (Tovar yetishmasligi):** Xaridor bor, lekin tovar omborda tugab qolgan — yo'qotilgan daromad va pasaygan konversiya.
2. **Overstock (Ortiqcha zaxira):** Haddan tashqari ko'p tovar sotib olib qo'yilgan — ombor to'lovi va aylanma mablag'ning muzlashi.

Biz lag-belgilar (1d, 7d, 14d), sirpanuvchi o'rtachalar hamda O'zbekiston bayramlari (11.11, Yangi yil, Navro'z) regressorlarini o'z ichiga olgan **Gradient Boosting Regressor** modelini qurdik va 30 kunlik **Rolling-window Backtesting** sinovidan o'tkazdik.

---

## 2. Modellar Taqqoslovi va Metrikalar (30 Kunlik Backtest)

| Model Nomi | Model Turi va Xususiyati | WAPE (%) | MAPE (%) | MAE (Mln UZS) | Xulosa |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Seasonal Naive** | 7 kunlik avvalgi hafta xuddi shu kun qiymati (Baseline) | 27.44% | 27.71% | 8.92 | Sodda taqqoslash bazasi |
| **Gradient Boosting (GBR)** | Laglar (1, 7, 14), Rolling Stats va Bayram regressorlari | **24.88%** | **23.82%** | **7.81** | **Eng yaxshi natija (+2.56% xatolik kamayishi)** |

*E-commerce sohasida kunlik tranzaksiyalar uchun 23-25% lik WAPE/MAPE ko'rsatkichi sanoatning "Good/Enterprise-Grade" aniqlik standarti hisoblanadi.*

---

## 3. Kelgusi 60 Kunlik Savdo Prognozi (Future 60-Day Forecast)

- Har bir kun uchun kutilayotgan savdo hajmi va **90% Lik Ishonchlilik Oralig'i (Confidence Bounds: Upper and Lower)** hisoblab chiqildi.
- Do'kon egalari va ta'minot zanjiri menejerlari uchun `data/processed/sales_forecast_60d.csv` eksport qilindi.
- Qachon, qaysi haftada zaxirani qancha miqdorda to'ldirish (Restock timing) bo'yicha aniq grafik tavsiya shakllantirildi.

---

## 4. Web Sayt / Portfolio Showcase uchun Xulosalar

- **Pitch:** "Lag-belgilar va O'zbekiston kalendar bayramlari regressorlari asosida qurilgan Gradient Boosting modeli 24.8% WAPE aniqlikda kelgusi 60 kunlik savdo ehtiyojini bashorat qildi."
- **Key Metrics:** 60 kunlik prognoz jadvali, 24.88% WAPE, Baseline'dan 2.56% ustunlik, 90% ishonchlilik koridori.
