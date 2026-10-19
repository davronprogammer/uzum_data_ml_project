"""
Uzum Market Pricing Engine & Price Elasticity of Demand (PED)
=============================================================
Ushbu modul narxning talabga sezgirligini (Price Elasticity of Demand - PED)
toifalar kesimida ekonometrik regression (Log-Log) usulida baholaydi hamda
daromadni maksimallashtiruvchi optimal narxlash strategiyasini ishlab chiqadi.
"""

import os
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any

UZUM_PURPLE = "#7000FF"
ACCENT_GREEN = "#00C853"
ACCENT_ORANGE = "#FF6D00"
ACCENT_BLUE = "#2979FF"

class UzumPricingEngine:
    """Narx elastikligi va narxni optimallashtirish klassi."""

    def __init__(
        self,
        db_path: str = "data/uzum_market.db",
        processed_dir: str = "data/processed",
        figures_dir: str = "reports/figures"
    ):
        self.db_path = db_path
        self.processed_dir = processed_dir
        self.figures_dir = figures_dir
        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(self.figures_dir, exist_ok=True)
        self._load_data()

    def _load_data(self):
        conn = sqlite3.connect(self.db_path)
        self.df_products = pd.read_sql_query("SELECT * FROM featured_products", conn)
        self.df_categories = pd.read_sql_query("SELECT * FROM categories", conn)
        conn.close()

    def estimate_elasticity_by_category(self, min_products_per_cat: int = 5) -> pd.DataFrame:
        """
        Log-Log Ekonometrik Regressiya orqali toifalar elastikligini hisoblash:
        ln(Quantity) = alpha + beta * ln(Price) + error
        Bu yerda beta = PED (Price Elasticity of Demand).
        """
        cat_counts = self.df_products.groupby("category_id")["product_id"].count()
        valid_cats = cat_counts[cat_counts >= min_products_per_cat].index

        results = []
        cat_names = self.df_categories.set_index("category_id")["category_name"].to_dict()

        for cid in valid_cats:
            sub = self.df_products[self.df_products["category_id"] == cid]
            # Narx va talab 0 dan katta bo'lishi kerak
            valid_rows = sub[(sub["price_current"] > 0) & (sub["orders_count"] > 0)]
            if len(valid_rows) < 4:
                continue

            ln_p = np.log(valid_rows["price_current"])
            ln_q = np.log(valid_rows["orders_count"])

            # Chiziqli regressiya qiyaligi (slope)
            cov_pq = np.cov(ln_p, ln_q)[0, 1]
            var_p = np.var(ln_p)
            if var_p == 0:
                continue

            ped = cov_pq / var_p

            # Elastiklik turini belgilash
            if ped < -1.2:
                elasticity_type = "Yuqori Elastik (Sezgir)"
                strategy = "Chegirma va promo orqali aylanmani oshirish tavsiya etiladi"
            elif -1.2 <= ped <= -0.8:
                elasticity_type = "Birlik Elastiklik"
                strategy = "Narx va talab mutanosib, narxni o'zgartirish xavfli"
            else:
                elasticity_type = "Noelastik (Sezuvchanlik past)"
                strategy = "Marjani oshirish uchun narxni 5-10% ko'tarish imkoniyati bor"

            results.append({
                "category_id": cid,
                "category_name": cat_names.get(cid, f"Category {cid}"),
                "products_count": len(valid_rows),
                "avg_price_uzs": int(valid_rows["price_current"].mean()),
                "avg_orders": int(valid_rows["orders_count"].mean()),
                "price_elasticity": round(ped, 2),
                "elasticity_type": elasticity_type,
                "pricing_strategy": strategy
            })

        df_ped = pd.DataFrame(results).sort_values("price_elasticity", ascending=True)

        # Saqlash
        csv_path = os.path.join(self.processed_dir, "price_elasticity_by_category.csv")
        df_ped.to_csv(csv_path, index=False, encoding="utf-8")

        conn = sqlite3.connect(self.db_path)
        df_ped.to_sql("price_elasticity_by_category", conn, if_exists="replace", index=False)
        conn.close()

        return df_ped

    def plot_pricing_analytics(self, df_ped: pd.DataFrame):
        """Narx elastikligi grafigini yaratish."""
        top_cats = pd.concat([df_ped.head(6), df_ped.tail(6)]).drop_duplicates()
        labels = [c[:22] for c in top_cats["category_name"]]

        fig, ax = plt.subplots(figsize=(12, 7))
        colors = [ACCENT_ORANGE if p < -1.0 else ACCENT_GREEN for p in top_cats["price_elasticity"]]
        bars = ax.barh(labels, top_cats["price_elasticity"], color=colors, alpha=0.85)
        ax.axvline(-1.0, color="red", linestyle="--", linewidth=1.5, label="Birlik elastiklik chegarasi (PED = -1.0)")
        ax.set_xlabel("Narx Elastikligi Koeffitsienti (PED)")
        
        for bar in bars:
            val = bar.get_width()
            ax.text(val - 0.05 if val < 0 else val + 0.05, bar.get_y() + bar.get_height()/2,
                    f"{val:.2f}", va="center", ha="right" if val < 0 else "left", fontweight="bold")

        plt.title("14.1. Uzum Market Toifalari Bo'yicha Narx Elastikligi (PED) va Narx Strategiyasi", pad=15)
        plt.legend(loc="lower right")
        plt.tight_layout()
        plt.savefig(f"{self.figures_dir}/14_01_price_elasticity_curve.png", dpi=300)
        plt.close()

    def run(self) -> pd.DataFrame:
        print("=== Narx Elastikligi va Strategiya Tahlili Boshlandi ===")
        df_ped = self.estimate_elasticity_by_category()
        self.plot_pricing_analytics(df_ped)
        print("=== Narx Tahlili Muvaffaqiyatli Yakunlandi ===")
        return df_ped

if __name__ == "__main__":
    pe = UzumPricingEngine()
    pe.run()
