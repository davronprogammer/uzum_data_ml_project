"""
Uzum Market Advanced Feature Engineering Engine
===============================================
Ushbu modul relyatsion ombordagi mahsulotlar, buyurtmalar va mijozlar
ma'lumotlaridan yangi biznes signallari, mashinaviy o'rganish (ML) va
chuqur tahlil uchun xususiyatlarni (Features) hisoblab chiqaradi.
"""

import logging
import math
import os
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("FeatureBuilder")

class UzumFeatureBuilder:
    """Feature Engineering pipeline klassi."""

    def __init__(
        self,
        db_path: str = "data/uzum_market.db",
        processed_dir: str = "data/processed"
    ):
        self.db_path = db_path
        self.processed_dir = processed_dir
        os.makedirs(self.processed_dir, exist_ok=True)

    def load_clean_data(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Bazadan toza jadvallarni o'qish."""
        conn = sqlite3.connect(self.db_path)
        df_products = pd.read_sql_query("SELECT * FROM products", conn)
        df_categories = pd.read_sql_query("SELECT * FROM categories", conn)
        df_orders = pd.read_sql_query("SELECT * FROM orders", conn)
        df_customers = pd.read_sql_query("SELECT * FROM customers", conn)
        conn.close()
        logger.info(f"Ma'lumotlar bazadan o'qildi: {len(df_products)} tovar, {len(df_orders)} buyurtma.")
        return df_products, df_categories, df_orders, df_customers

    # ==========================================
    # 1. PRODUCT FEATURES
    # ==========================================
    def build_product_features(
        self,
        df_products: pd.DataFrame,
        df_categories: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Mahsulotlar uchun ilg'or belgilarni hisoblash:
        - Bayesian Average Rating (IMDB / Amazon formulasi)
        - Nisbiy narx indeksi va narx segmentatsiyasi
        - Chegirma chuqurligi darajalari (Discount Depth Tiers)
        """
        logger.info("Mahsulotlar belgilari (Product Features) hisoblanmoqda...")
        df = df_products.copy()

        # A. Bayesian Average Rating: WR = (v / (v + m)) * R + (m / (v + m)) * C
        # R = mahsulot reytingi, v = sharhlar soni
        # C = katalogning o'rtacha reytingi, m = minimal sharhlar chegarasi (kvantil)
        C = df["rating"].mean()
        m = df["reviews_count"].quantile(0.65)  # 65-persentil
        if m < 5:
            m = 5.0

        df["bayesian_rating"] = (
            (df["reviews_count"] / (df["reviews_count"] + m)) * df["rating"]
            + (m / (df["reviews_count"] + m)) * C
        ).round(2)

        # B. Kategoriya bo'yicha o'rtacha narx va Nisbiy narx indeksi
        cat_avg_price = df.groupby("category_id")["price_current"].transform("mean")
        df["category_mean_price"] = cat_avg_price.round(0)
        df["price_relative_ratio"] = (df["price_current"] / df["category_mean_price"]).round(2)

        # C. Narx segmenti
        # Budget (< 0.7x), Mid-range (0.7x - 1.3x), Premium (> 1.3x)
        conditions = [
            (df["price_relative_ratio"] < 0.70),
            (df["price_relative_ratio"].between(0.70, 1.30)),
            (df["price_relative_ratio"] > 1.30)
        ]
        choices = ["Budget", "Mid-Range", "Premium"]
        df["price_segment"] = np.select(conditions, choices, default="Mid-Range")

        # D. Chegirma chuqurligi darajalari
        discount_conditions = [
            (df["discount_percentage"] == 0),
            (df["discount_percentage"] < 15),
            (df["discount_percentage"].between(15, 30)),
            (df["discount_percentage"] > 30)
        ]
        discount_choices = ["No Discount", "Low (1-15%)", "Moderate (15-30%)", "Deep (>30%)"]
        df["discount_tier"] = np.select(discount_conditions, discount_choices, default="No Discount")

        # E. Oylik to'lov yuki (Installment burden ratio)
        df["installment_fraction"] = np.where(
            df["price_current"] > 0,
            (df["monthly_installment"] / df["price_current"]).round(4),
            0.0
        )

        logger.info("Mahsulotlar belgilari muvaffaqiyatli hisoblandi.")
        return df

    # ==========================================
    # 2. ORDER & TEMPORAL FEATURES
    # ==========================================
    def build_order_features(self, df_orders: pd.DataFrame) -> pd.DataFrame:
        """
        Buyurtmalar va vaqtli belgilar (Temporal Features):
        - Hafta kuni, oy, soat, dam olish kuni flagi
        - O'zbekiston bayramlari va maxsus savdo kampaniyalari flagi
        """
        logger.info("Buyurtmalar va vaqt belgilari (Order & Temporal Features) hisoblanmoqda...")
        df = df_orders.copy()
        df["order_datetime"] = pd.to_datetime(df["order_date"])

        df["order_year"] = df["order_datetime"].dt.year
        df["order_month"] = df["order_datetime"].dt.month
        df["order_day"] = df["order_datetime"].dt.day
        df["order_hour"] = df["order_datetime"].dt.hour
        df["day_of_week"] = df["order_datetime"].dt.day_name()
        df["is_weekend"] = df["order_datetime"].dt.weekday.isin([5, 6]).astype(int)

        # O'zbekiston savdo aksiyalari va mavsumiy piklar
        def is_campaign_period(row):
            m, d = row["order_month"], row["order_day"]
            # 11.11 Jahon savdo kuni
            if m == 11 and 9 <= d <= 13:
                return "11.11 Mega Sale"
            # Yangi yil arafasi
            if m == 12 and d >= 20:
                return "New Year Shopping"
            # 8-mart
            if m == 3 and 1 <= d <= 8:
                return "Women's Day"
            # Navro'z
            if m == 3 and 16 <= d <= 22:
                return "Navruz"
            # Maktab bozori (Back to school)
            if (m == 8 and d >= 20) or (m == 9 and d <= 5):
                return "Back to School"
            return "Regular Day"

        df["campaign_period"] = df.apply(is_campaign_period, axis=1)
        df["is_special_campaign"] = (df["campaign_period"] != "Regular Day").astype(int)

        logger.info("Buyurtmalar belgilari muvaffaqiyatli hisoblandi.")
        return df

    # ==========================================
    # 3. CUSTOMER RFM BASE FEATURES
    # ==========================================
    def build_customer_features(
        self,
        df_customers: pd.DataFrame,
        df_orders: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Mijozlar profilingi va RFM bazaviy belgilari:
        - Recency (oxirgi buyurtmadan o'tgan kunlar soni)
        - Frequency (buyurtmalar soni)
        - Monetary (umumiy xarid summasi)
        - AOV (Average Order Value)
        - Sevimli to'lov usuli
        """
        logger.info("Mijozlar belgilari (Customer RFM Features) hisoblanmoqda...")
        df = df_customers.copy()
        
        # Referent tahlil sanasi (eng oxirgi buyurtma sanasidan 1 kun keyingi sana)
        max_date = pd.to_datetime(df_orders["order_date"]).max()
        analysis_date = max_date + pd.Timedelta(days=1)

        df["last_order_datetime"] = pd.to_datetime(df["last_order_date"])
        df["recency_days"] = (analysis_date - df["last_order_datetime"]).dt.days

        # AOV hisoblash
        df["aov"] = np.where(
            df["total_orders"] > 0,
            (df["total_spent"] / df["total_orders"]).round(0),
            0
        )

        # Mijozning eng ko'p ishlatgan to'lov turi
        pref_payment = df_orders.groupby("customer_id")["payment_method"].agg(
            lambda x: x.mode().iloc[0] if not x.empty else "Uzum Pay"
        ).reset_index().rename(columns={"payment_method": "preferred_payment_method"})

        df = df.merge(pref_payment, on="customer_id", how="left")

        logger.info("Mijozlar belgilari muvaffaqiyatli hisoblandi.")
        return df

    def run(self) -> None:
        """Barcha belgilarni ishlab chiqarish va saqlash."""
        logger.info("=== Feature Engineering Pipeline Boshlandi ===")
        df_products, df_categories, df_orders, df_customers = self.load_clean_data()

        feat_products = self.build_product_features(df_products, df_categories)
        feat_orders = self.build_order_features(df_orders)
        feat_customers = self.build_customer_features(df_customers, feat_orders)

        # A. CSV formatida saqlash
        prod_path = os.path.join(self.processed_dir, "featured_products.csv")
        ord_path = os.path.join(self.processed_dir, "featured_orders.csv")
        cust_path = os.path.join(self.processed_dir, "featured_customers.csv")

        feat_products.to_csv(prod_path, index=False, encoding="utf-8")
        feat_orders.to_csv(ord_path, index=False, encoding="utf-8")
        feat_customers.to_csv(cust_path, index=False, encoding="utf-8")
        logger.info(f"Feature CSV fayllar saqlandi: {prod_path}, {ord_path}, {cust_path}")

        # B. SQLite bazasiga yangi featured jadvallarni yuklash
        conn = sqlite3.connect(self.db_path)
        feat_products.to_sql("featured_products", conn, if_exists="replace", index=False)
        feat_orders.to_sql("featured_orders", conn, if_exists="replace", index=False)
        feat_customers.to_sql("featured_customers", conn, if_exists="replace", index=False)
        conn.commit()
        conn.close()
        logger.info(f"SQLite bazasida yangi 'featured_*' jadvallari yaratildi.")
        logger.info("=== Feature Engineering Pipeline Muvaffaqiyatli Yakunlandi ===")

if __name__ == "__main__":
    builder = UzumFeatureBuilder()
    builder.run()
