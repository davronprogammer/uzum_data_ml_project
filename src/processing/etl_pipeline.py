"""
Uzum Market Production ETL Pipeline
===================================
Ushbu modul data/raw papkasidagi xom JSON ma'lumotlarni o'qiydi (Extract),
tozalaydi, validatsiyadan o'tkazadi va normallashtiradi (Transform),
so'ngra SQLite relyatsion bazasiga va data/processed analitik fayllariga
yuklaydi (Load).
"""

import json
import logging
import math
import os
import sqlite3
import pandas as pd
from typing import Dict, List, Any, Tuple
from datetime import datetime

from src.database.schema import ALL_TABLES, INDEXES

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ETLPipeline")

class UzumETLPipeline:
    """End-to-End Extract-Transform-Load pipeline klassi."""

    def __init__(
        self,
        raw_catalog_path: str = "data/raw/uzum_catalog_raw.json",
        raw_orders_path: str = "data/raw/uzum_orders_raw.json",
        db_path: str = "data/uzum_market.db",
        processed_dir: str = "data/processed"
    ):
        self.raw_catalog_path = raw_catalog_path
        self.raw_orders_path = raw_orders_path
        self.db_path = db_path
        self.processed_dir = processed_dir
        os.makedirs(self.processed_dir, exist_ok=True)

    # ==========================================
    # 1. EXTRACT
    # ==========================================
    def extract_raw_data(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Xom JSON fayllarni xotiraga yuklash."""
        logger.info("--- 1. EXTRACT BOSQICHI ---")
        if not os.path.exists(self.raw_catalog_path):
            raise FileNotFoundError(f"Katalog fayli topilmadi: {self.raw_catalog_path}")
        if not os.path.exists(self.raw_orders_path):
            raise FileNotFoundError(f"Buyurtmalar fayli topilmadi: {self.raw_orders_path}")

        with open(self.raw_catalog_path, "r", encoding="utf-8") as f:
            catalog_raw = json.load(f)
        with open(self.raw_orders_path, "r", encoding="utf-8") as f:
            orders_raw = json.load(f)

        logger.info(f"Yuklandi: {len(catalog_raw)} ta tovar, {len(orders_raw)} ta buyurtma.")
        return catalog_raw, orders_raw

    # ==========================================
    # 2. TRANSFORM
    # ==========================================
    def transform_data(
        self,
        catalog_raw: List[Dict[str, Any]],
        orders_raw: List[Dict[str, Any]]
    ) -> Dict[str, pd.DataFrame]:
        """Ma'lumotlarni tozalash, normallashtirish va tekshirish."""
        logger.info("--- 2. TRANSFORM BOSQICHI ---")

        # A. Kategoriyalarni ajratish
        categories_dict = {}
        cleaned_products = []

        for p in catalog_raw:
            cat_id = p.get("category_id") or 99999
            cat_name = p.get("category_name") or "Boshqa"
            categories_dict[cat_id] = cat_name

            # Mahsulot tozalash
            price_curr = int(p.get("price_current", 0) or 0)
            price_orig = int(p.get("price_original", 0) or price_curr)
            if price_orig < price_curr:
                price_orig = price_curr

            disc_pct = float(p.get("discount_percentage", 0.0) or 0.0)
            if price_orig > price_curr and disc_pct == 0.0 and price_orig > 0:
                disc_pct = round(((price_orig - price_curr) / price_orig) * 100, 2)

            has_inst = bool(p.get("has_installment", False))
            monthly_inst = int(p.get("monthly_installment", 0) or 0)
            if has_inst and monthly_inst == 0 and price_curr > 0:
                monthly_inst = math.ceil(price_curr / 12)

            cleaned_products.append({
                "product_id": int(p["product_id"]),
                "title": str(p.get("title", "")).strip(),
                "category_id": int(cat_id),
                "price_current": price_curr,
                "price_original": price_orig,
                "discount_percentage": disc_pct,
                "monthly_installment": monthly_inst,
                "has_installment": 1 if has_inst else 0,
                "rating": float(p.get("rating", 0.0) or 0.0),
                "reviews_count": int(p.get("reviews_count", 0) or 0),
                "orders_count": int(p.get("orders_count", 0) or 0),
                "is_eco": 1 if p.get("is_eco") else 0,
                "is_adult": 1 if p.get("is_adult") else 0,
                "delivery_time_days": int(p.get("delivery_time_days", 1) or 1),
                "delivery_type": str(p.get("delivery_type", "PVZ")),
                "crawled_at": str(p.get("crawled_at", datetime.now().isoformat()))
            })

        df_categories = pd.DataFrame([
            {"category_id": cid, "category_name": cname}
            for cid, cname in categories_dict.items()
        ]).drop_duplicates(subset=["category_id"])

        df_products = pd.DataFrame(cleaned_products).drop_duplicates(subset=["product_id"])

        # B. Buyurtmalar va savatcha tovarlarini normallashtirish
        cleaned_orders = []
        cleaned_order_items = []
        customer_spends: Dict[str, Dict[str, Any]] = {}

        for o in orders_raw:
            oid = str(o["order_id"])
            cid = str(o["customer_id"])
            odt = str(o["order_date"])
            tot = int(o["total_amount"])

            cleaned_orders.append({
                "order_id": oid,
                "customer_id": cid,
                "order_date": odt,
                "region": str(o.get("region", "Toshkent shahri")),
                "delivery_type": str(o.get("delivery_type", "PVZ")),
                "payment_method": str(o.get("payment_method", "Uzum Pay")),
                "status": str(o.get("status", "Delivered")),
                "items_count": int(o.get("items_count", 1)),
                "total_amount": tot
            })

            # Mijozlar agregatsiyasi
            if cid not in customer_spends:
                customer_spends[cid] = {
                    "customer_id": cid,
                    "region": o.get("region", "Toshkent shahri"),
                    "first_order_date": odt,
                    "last_order_date": odt,
                    "total_orders": 0,
                    "total_spent": 0
                }
            customer_spends[cid]["total_orders"] += 1
            customer_spends[cid]["total_spent"] += tot
            if odt < customer_spends[cid]["first_order_date"]:
                customer_spends[cid]["first_order_date"] = odt
            if odt > customer_spends[cid]["last_order_date"]:
                customer_spends[cid]["last_order_date"] = odt

            # Ichki savatcha tovarlari
            for itm in o.get("items", []):
                cleaned_order_items.append({
                    "order_id": oid,
                    "product_id": int(itm["product_id"]),
                    "quantity": int(itm.get("quantity", 1)),
                    "unit_price": int(itm.get("unit_price", 0)),
                    "line_total": int(itm.get("line_total", 0))
                })

        df_orders = pd.DataFrame(cleaned_orders).drop_duplicates(subset=["order_id"])
        df_order_items = pd.DataFrame(cleaned_order_items)
        df_customers = pd.DataFrame(list(customer_spends.values())).drop_duplicates(subset=["customer_id"])

        logger.info(f"Transform natijasi:")
        logger.info(f" - Kategoriyalar: {len(df_categories)}")
        logger.info(f" - Mahsulotlar: {len(df_products)}")
        logger.info(f" - Mijozlar: {len(df_customers)}")
        logger.info(f" - Buyurtmalar: {len(df_orders)}")
        logger.info(f" - Savatcha satrlari: {len(df_order_items)}")

        return {
            "categories": df_categories,
            "products": df_products,
            "customers": df_customers,
            "orders": df_orders,
            "order_items": df_order_items
        }

    # ==========================================
    # 3. LOAD
    # ==========================================
    def load_data(self, dfs: Dict[str, pd.DataFrame]) -> None:
        """Ma'lumotlar bazasiga (SQLite) va processed CSV'larga yuklash."""
        logger.info("--- 3. LOAD BOSQICHI ---")
        
        # A. SQLite omboriga yuklash
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Sxemalarni yaratish
        for table_name, ddl in ALL_TABLES:
            cursor.execute(ddl)

        # Jadvallarni yuklash
        for table_name, df in dfs.items():
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            logger.info(f"Database jadvaliga yuklandi: '{table_name}' ({len(df)} qator)")

        # Indekslarni yaratish
        for idx_sql in INDEXES:
            try:
                cursor.execute(idx_sql)
            except Exception as e:
                logger.warning(f"Indeks yaratishda ogohlantirish: {e}")

        conn.commit()
        conn.close()
        logger.info(f"SQLite relyatsion ma'lumotlar bazasi saqlandi: {self.db_path}")

        # B. Tahliliy toza CSV formatlarida saqlash (data/processed/)
        for name, df in dfs.items():
            csv_path = os.path.join(self.processed_dir, f"clean_{name}.csv")
            df.to_csv(csv_path, index=False, encoding="utf-8")
            logger.info(f"Processed CSV saqlandi: {csv_path}")

    def run(self) -> None:
        """Butun ETL jarayonini bajarish."""
        logger.info("=== Uzum Market ETL Pipeline Boshlandi ===")
        catalog_raw, orders_raw = self.extract_raw_data()
        dfs = self.transform_data(catalog_raw, orders_raw)
        self.load_data(dfs)
        logger.info("=== Uzum Market ETL Pipeline Muvaffaqiyatli Yakunlandi ===")

if __name__ == "__main__":
    pipeline = UzumETLPipeline()
    pipeline.run()
