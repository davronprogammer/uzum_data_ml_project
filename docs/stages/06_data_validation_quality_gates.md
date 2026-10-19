# Stage 06: Data Validation & Quality Gates

> **Kategoriya:** Data Quality, Governance & Unit Testing  
> **Status:** Muvaffaqiyatli yakunlandi ✅  
> **Test moduli:** `tests/test_data_quality.py`  
> **Natija:** 7/7 Tests Passed in 0.082s (100% Success)

---

## 1. Muammo va Sifat Madaniyati

Ko'p junior data loyihalarida model xato ishlashining asl sababi algoritmda emas, balki ma'lumotlar sifatidagi yashirin nuqsonlarda bo'ladi:
- Takroriy identifikatorlar (Duplicate IDs);
- Manfiy yoki nol narxlar;
- Buyurtmasi mavjud bo'lmagan yetim tovarlar (Orphan foreign keys);
- Buyurtmaning umumiy summasi ichki tovarlar yig'indisiga mos kelmasligi (Financial drift).

Biz barcha ma'lumotlarni production'ga o'tkazishdan oldin **7 ta avtomatlashtirilgan sifat eshiklari (Quality Gates)** bilan himoyaladik.

---

## 2. Testlar Majmuasi va Natijalari

| # | Test Nomi | Maqsad va Tekshiruv Sharti | Natija |
| :--- | :--- | :--- | :--- |
| **1** | `test_products_primary_key_uniqueness` | `product_id` bo'yicha dublikatlar soni = 0 | **PASSED** (0 dublikat) |
| **2** | `test_orders_primary_key_uniqueness` | `order_id` bo'yicha dublikatlar soni = 0 | **PASSED** (0 dublikat) |
| **3** | `test_customers_primary_key_uniqueness` | `customer_id` bo'yicha dublikatlar soni = 0 | **PASSED** (0 dublikat) |
| **4** | `test_price_and_discount_constraints` | `price > 0` va `0 <= discount <= 100` | **PASSED** (100% to'g'ri) |
| **5** | `test_ratings_boundary` | `0.0 <= rating <= 5.0` chegarasi | **PASSED** (100% to'g'ri) |
| **6** | `test_referential_integrity_order_items` | Har bir savatcha tovari mavjud buyurtmaga birikkanligi | **PASSED** (0 ta yetim yozuv) |
| **7** | `test_financial_reconciliation` | `orders.total_amount == SUM(order_items.line_total)` | **PASSED** (Moliya balansi 100% mos) |

---

## 3. Web Sayt / Portfolio Showcase uchun Xulosalar

- **Pitch:** "Ishonchli va buzilmas tahlil kafolati: 7 darajali avtomatik Data Quality Gates sinovi 0.08 soniyada 100% muvaffaqiyat bilan yakunlandi."
- **Key Metrics:** 7/7 test passed, 0 data anomalies, 0 financial mismatches.
