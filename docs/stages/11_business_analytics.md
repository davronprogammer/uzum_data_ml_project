# Stage 11: Business Analytics & Unit Economics

> **Kategoriya:** Financial & Executive Business Intelligence  
> **Status:** Muvaffaqiyatli yakunlandi ✅  
> **Modul:** `src/analytics/business_metrics.py`  
> **Test:** `tests/test_domain_analytics.py` (Passed)

---

## 1. Nima Uchun Unit Economics va Boshqaruv KPILari Muhim?

Har qanday Data Science loyihasi oxir-oqibat kompaniya balansida (P&L - Profit and Loss) aks etishi kerak. Mahsulot qanchalik ko'p sotilmasin, agar bitta buyurtma (Unit) darajasida logistika, to'lov xarajatlari va qaytarilishlar hisobga olinmasa, kompaniya har bir sotuvdan zarar ko'rishi mumkin.

Biz Uzum Market platformasi uchun to'liq moliya va Unit Economics modelini qurdik.

---

## 2. Boshqaruv KPILari (Executive Dashboard Metrics)

| KPI Ko'rsatkichi | Qiymat | Biznes Talqini |
| :--- | :--- | :--- |
| **Gross GMV (Umumiy Savdo Aylanmasi)** | **12.56 Milliard UZS** | Platforma orqali amalga oshirilgan umumiy aylanma |
| **Net GMV (Yetkazilgan Savdo)** | **11.51 Milliard UZS** | Muvaffaqiyatli topshirilgan buyurtmalar hajmi |
| **Gross AOV (O'rtacha Buyurtma)** | **742,407 UZS** | Bitta savatning o'rtacha qiymati |
| **Marketplace Take-Rate (15%)** | **1.73 Milliard UZS** | Uzum Market olgan sof platforma komissiyasi |
| **Buyurtmani Bekor Qilish (Cancellation)**| **5.07%** | Xaridor yoki sotuvchi tomonidan bekor qilingan |
| **Qaytarishlar Ulushi (Return Rate)** | **3.16%** | PVZda tovardan voz kechish yoki nuqson sababli |
| **Top 20% Toifalar Aylanma Ulushi** | **86.28%** | **Pareto 80/20 qoidasi:** 20% toifalar aylanmaning 86% ini beradi |

---

## 3. Bitta Buyurtma Darajasidagi Unit Economics (Per-Order Breakdown)

```text
+-------------------------------------------------------------+
| O'rtacha Buyurtma Qiymati (AOV):              741,271 UZS  |
|                                                             |
|  [+] Uzum Komissiyasi (Take-Rate 15%):        111,190 UZS  |
|  [-] To'lov tizimlari xarajati (Acquiring):   -11,119 UZS  |
|  [-] Bepul PVZ yetkazib berish (Logistika):   -15,000 UZS  |
| ----------------------------------------------------------- |
|  [=] Sof Operatsion Foyda (Contribution):      85,071 UZS  |
|  [★] Contribution Margin:                          76.51%  |
+-------------------------------------------------------------+
```

---

## 4. Web Sayt / Portfolio Showcase uchun Xulosalar

- **Pitch:** "Platformaning 12.56 milliard so'mlik aylanmasi tahlil qilinib, har bir buyurtma uchun 85,071 so'mlik sof Contribution Margin ta'minlaydigan Unit Economics modeli ishlab chiqildi."
- **Key Metrics:** 12.56 mlrd UZS GMV, 1.73 mlrd UZS sof komissiya, 76.5% Contribution margin, 86.3% Pareto konsentratsiyasi.
