"""
Uzum Market Feature Engineering Test Suite
==========================================
Ushbu modul hisoblangan belgilarning (Features) matematik va mantiqiy
to'g'riligini avtomatlashtirilgan testlar orqali tekshiradi.
"""

import sqlite3
import unittest
import pandas as pd
import os

DB_PATH = "data/uzum_market.db"

class TestFeatureEngineering(unittest.TestCase):
    """Belgilar to'g'riligini tekshiruvchi test klassi."""

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError(f"Database fayli topilmadi: {DB_PATH}")
        cls.conn = sqlite3.connect(DB_PATH)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_bayesian_rating_validity(self):
        """1. Bayesian rating hisoblanishi va chegaralarini tekshirish."""
        df = pd.read_sql_query("SELECT bayesian_rating, rating, reviews_count FROM featured_products", self.conn)
        self.assertFalse(df["bayesian_rating"].isnull().any(), "Bayesian rating ustunida NaN qiymat mavjud!")
        self.assertTrue((df["bayesian_rating"] >= 0.0).all() and (df["bayesian_rating"] <= 5.0).all(), "Bayesian rating [0, 5] oralig'ida emas!")

    def test_price_segments_and_ratios(self):
        """2. Narx nisbati va segmentlar to'g'riligini tekshirish."""
        df = pd.read_sql_query("SELECT price_relative_ratio, price_segment FROM featured_products", self.conn)
        self.assertTrue((df["price_relative_ratio"] > 0).all(), "Nisbiy narx indeksi 0 dan katta bo'lishi shart!")
        valid_segments = {"Budget", "Mid-Range", "Premium"}
        self.assertTrue(set(df["price_segment"].unique()).issubset(valid_segments), "Noma'lum narx segmenti aniqlandi!")

    def test_discount_tiers(self):
        """3. Chegirma darajalari to'g'ri taqsimlanganini tekshirish."""
        df = pd.read_sql_query("SELECT discount_tier FROM featured_products", self.conn)
        valid_tiers = {"No Discount", "Low (1-15%)", "Moderate (15-30%)", "Deep (>30%)"}
        self.assertTrue(set(df["discount_tier"].unique()).issubset(valid_tiers), "Noma'lum chegirma darajasi topildi!")

    def test_order_temporal_features(self):
        """4. Buyurtmalar vaqt belgilari (soat, kun, dam olish kuni) to'g'riligini tekshirish."""
        df = pd.read_sql_query("SELECT order_hour, is_weekend, is_special_campaign FROM featured_orders", self.conn)
        self.assertTrue((df["order_hour"].between(0, 23)).all(), "Soatlar 0..23 oralig'ida bo'lishi shart!")
        self.assertTrue(set(df["is_weekend"].unique()).issubset({0, 1}), "is_weekend faqat 0 yoki 1 bo'lishi kerak!")
        self.assertTrue(set(df["is_special_campaign"].unique()).issubset({0, 1}), "is_special_campaign faqat 0 yoki 1 bo'lishi kerak!")

    def test_customer_rfm_metrics(self):
        """5. Mijozlar Recency, AOV va to'lov turi to'g'riligini tekshirish."""
        df = pd.read_sql_query("SELECT recency_days, aov, preferred_payment_method FROM featured_customers", self.conn)
        self.assertTrue((df["recency_days"] >= 0).all(), "Recency kunlari manfiy bo'lishi mumkin emas!")
        self.assertTrue((df["aov"] >= 0).all(), "O'rtacha chek (AOV) manfiy bo'lishi mumkin emas!")
        self.assertFalse(df["preferred_payment_method"].isnull().any(), "Sevimli to'lov turi bo'sh qolgan!")

if __name__ == "__main__":
    unittest.main()
