"""
Uzum Market Automated Data Quality & Validation Suite
=====================================================
Ushbu test to'plami relyatsion ma'lumotlar bazasidagi ma'lumotlar yaxlitligi
va sifatini (Data Integrity, Referential Integrity, Logical Constraints)
avtomatik tarzda tekshiradi.
"""

import sqlite3
import unittest
import pandas as pd
import os

DB_PATH = "data/uzum_market.db"

class TestDataQuality(unittest.TestCase):
    """Ma'lumotlar sifati va kontraktlarini tekshiruvchi test klassi."""

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError(f"Database fayli topilmadi: {DB_PATH}")
        cls.conn = sqlite3.connect(DB_PATH)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_products_primary_key_uniqueness(self):
        """1. Mahsulotlar IDlari unikal va bo'sh emasligini tekshirish."""
        df = pd.read_sql_query("SELECT product_id, COUNT(*) as cnt FROM products GROUP BY product_id HAVING cnt > 1", self.conn)
        self.assertEqual(len(df), 0, "Mahsulotlar jadvalida takrorlangan product_id mavjud!")

    def test_orders_primary_key_uniqueness(self):
        """2. Buyurtmalar IDlari unikal va bo'sh emasligini tekshirish."""
        df = pd.read_sql_query("SELECT order_id, COUNT(*) as cnt FROM orders GROUP BY order_id HAVING cnt > 1", self.conn)
        self.assertEqual(len(df), 0, "Buyurtmalar jadvalida takrorlangan order_id mavjud!")

    def test_customers_primary_key_uniqueness(self):
        """3. Mijozlar IDlari unikal va bo'sh emasligini tekshirish."""
        df = pd.read_sql_query("SELECT customer_id, COUNT(*) as cnt FROM customers GROUP BY customer_id HAVING cnt > 1", self.conn)
        self.assertEqual(len(df), 0, "Mijozlar jadvalida takrorlangan customer_id mavjud!")

    def test_price_and_discount_constraints(self):
        """4. Narxlar > 0 va chegirmalar 0..100 oralig'ida ekanligini tekshirish."""
        df_invalid_price = pd.read_sql_query("SELECT * FROM products WHERE price_current <= 0", self.conn)
        self.assertEqual(len(df_invalid_price), 0, "Manfiy yoki 0 narxga ega tovarlar topildi!")

        df_invalid_disc = pd.read_sql_query("SELECT * FROM products WHERE discount_percentage < 0 OR discount_percentage > 100", self.conn)
        self.assertEqual(len(df_invalid_disc), 0, "Chegirma foizi [0, 100] oralig'idan tashqariga chiqib ketgan!")

    def test_ratings_boundary(self):
        """5. Reytinglar [0.0, 5.0] oralig'ida ekanligini tekshirish."""
        df_invalid_rating = pd.read_sql_query("SELECT * FROM products WHERE rating < 0.0 OR rating > 5.0", self.conn)
        self.assertEqual(len(df_invalid_rating), 0, "Noto'g'ri reyting qiymatlari aniqlandi!")

    def test_referential_integrity_order_items(self):
        """6. Savatchadagi har bir tovar mavjud buyurtmaga biriktirilganligini tekshirish (FK)."""
        df_orphan_items = pd.read_sql_query("""
            SELECT oi.order_id 
            FROM order_items oi 
            LEFT JOIN orders o ON oi.order_id = o.order_id 
            WHERE o.order_id IS NULL
        """, self.conn)
        self.assertEqual(len(df_orphan_items), 0, "Egasiz (orphan) savatcha tovarlari topildi!")

    def test_financial_reconciliation(self):
        """7. Buyurtma umumiy summasi uning ichidagi tovarlar yig'indisiga tengligini tekshirish."""
        df_mismatch = pd.read_sql_query("""
            SELECT o.order_id, o.total_amount, SUM(oi.line_total) as items_sum
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY o.order_id, o.total_amount
            HAVING o.total_amount != SUM(oi.line_total)
        """, self.conn)
        self.assertEqual(len(df_mismatch), 0, "Moliya hisobida tafovut aniqlandi: buyurtma summasi tovarlar yig'indisiga teng emas!")

if __name__ == "__main__":
    unittest.main()
