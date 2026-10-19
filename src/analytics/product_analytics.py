"""
Uzum Market Product Assortment (ABC/XYZ) & Market Basket Analysis (MBA)
=======================================================================
Ushbu modul tovarlarni aylanma (ABC) va barqarorlik (XYZ) bo'yicha 9 ta
katakka segmentatsiya qiladi hamda birgalikda xarid qilinadigan tovarlar
uchun assotsiativ qoidalarni (Support, Confidence, Lift) hisoblaydi.
"""

import os
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple, Dict

UZUM_PURPLE = "#7000FF"
ACCENT_GREEN = "#00C853"
ACCENT_ORANGE = "#FF6D00"
ACCENT_BLUE = "#2979FF"

class UzumProductAnalytics:
    """Mahsulotlar assortimenti va savatcha tahlili klassi."""

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
        self.df_orders = pd.read_sql_query("SELECT * FROM featured_orders", conn)
        self.df_order_items = pd.read_sql_query("SELECT * FROM order_items", conn)
        conn.close()

    def compute_abc_xyz_matrix(self) -> pd.DataFrame:
        """ABC/XYZ matritsasini hisoblash."""
        # 1. Tovarlarning umumiy daromadi (Revenue) va sotuv variatsiyasini hisoblash
        prod_revenue = self.df_order_items.groupby("product_id").agg(
            total_revenue=("line_total", "sum"),
            total_units=("quantity", "sum"),
            orders_count=("order_id", "nunique"),
            std_quantity=("quantity", "std"),
            mean_quantity=("quantity", "mean")
        ).reset_index()

        df = self.df_products.merge(prod_revenue, on="product_id", how="left").fillna(0)

        # ABC Tahlili (Kumulyativ daromad ulushi bo'yicha)
        df = df.sort_values("total_revenue", ascending=False)
        total_market_rev = df["total_revenue"].sum()
        df["revenue_share"] = df["total_revenue"] / total_market_rev if total_market_rev > 0 else 0
        df["cumulative_revenue_share"] = df["revenue_share"].cumsum()

        def assign_abc(cum_share):
            if cum_share <= 0.80:
                return "A"
            elif cum_share <= 0.95:
                return "B"
            else:
                return "C"

        df["abc_class"] = df["cumulative_revenue_share"].apply(assign_abc)

        # XYZ Tahlili (Talabning noaniqlik koeffitsienti CV = std / mean)
        # CV qancha kichik bo'lsa, talab shuncha barqaror (X)
        df["cv_demand"] = np.where(df["mean_quantity"] > 0, df["std_quantity"] / df["mean_quantity"], 0.5)

        def assign_xyz(cv):
            if cv <= 0.15:
                return "X"
            elif cv <= 0.35:
                return "Y"
            else:
                return "Z"

        df["xyz_class"] = df["cv_demand"].apply(assign_xyz)
        df["abc_xyz_segment"] = df["abc_class"] + df["xyz_class"]

        # Saqlash
        csv_path = os.path.join(self.processed_dir, "product_abc_xyz_analysis.csv")
        df.to_csv(csv_path, index=False, encoding="utf-8")

        conn = sqlite3.connect(self.db_path)
        df.to_sql("product_abc_xyz_analysis", conn, if_exists="replace", index=False)
        conn.close()

        return df

    def compute_market_basket_analysis(self, min_support_count: int = 5) -> pd.DataFrame:
        """
        Market Basket Analysis (Apriori qoidalari):
        Bir buyurtmada birga xarid qilingan tovarlar juftligi bo'yicha:
        - Support: P(A & B)
        - Confidence: P(B | A)
        - Lift: P(A & B) / (P(A) * P(B))
        """
        # Faqat 2 yoki undan ortiq tovar olingan savatchalarni tanlaymiz
        basket_counts = self.df_order_items.groupby("order_id")["product_id"].count()
        multi_item_orders = basket_counts[basket_counts > 1].index

        df_multi = self.df_order_items[self.df_order_items["order_id"].isin(multi_item_orders)]
        total_baskets = len(multi_item_orders)

        # Har bir tovarning individual uchrash soni (Support count)
        item_support = df_multi.groupby("product_id")["order_id"].nunique().to_dict()

        # Birgalikda xarid qilingan juftliklarni (Self-Join orqali) hisoblash
        merged = df_multi.merge(df_multi, on="order_id", suffixes=("_A", "_B"))
        pairs = merged[merged["product_id_A"] < merged["product_id_B"]]

        pair_counts = pairs.groupby(["product_id_A", "product_id_B"])["order_id"].nunique().reset_index()
        pair_counts.columns = ["product_id_A", "product_id_B", "pair_count"]
        pair_counts = pair_counts[pair_counts["pair_count"] >= min_support_count]

        # Nomlarni birlashtirish
        prod_titles = self.df_products.set_index("product_id")["title"].to_dict()
        pair_counts["title_A"] = pair_counts["product_id_A"].map(prod_titles)
        pair_counts["title_B"] = pair_counts["product_id_B"].map(prod_titles)

        # Metrikalarni hisoblash
        pair_counts["support"] = pair_counts["pair_count"] / total_baskets
        pair_counts["confidence_A_to_B"] = pair_counts["pair_count"] / pair_counts["product_id_A"].map(item_support)
        pair_counts["confidence_B_to_A"] = pair_counts["pair_count"] / pair_counts["product_id_B"].map(item_support)

        # Lift = P(A & B) / (P(A) * P(B))
        p_A = pair_counts["product_id_A"].map(item_support) / total_baskets
        p_B = pair_counts["product_id_B"].map(item_support) / total_baskets
        pair_counts["lift"] = (pair_counts["support"] / (p_A * p_B)).round(2)

        pair_counts = pair_counts.sort_values("lift", ascending=False)

        # Saqlash
        csv_path = os.path.join(self.processed_dir, "market_basket_rules.csv")
        pair_counts.to_csv(csv_path, index=False, encoding="utf-8")

        return pair_counts

    def plot_analytics(self, df_abc_xyz: pd.DataFrame, mba_rules: pd.DataFrame):
        """ABC/XYZ va MBA vizualizatsiyalarini yaratish."""
        # 1. ABC/XYZ Heatmap
        matrix_counts = pd.crosstab(df_abc_xyz["abc_class"], df_abc_xyz["xyz_class"]).reindex(
            index=["A", "B", "C"], columns=["X", "Y", "Z"]
        ).fillna(0)

        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(matrix_counts, annot=True, fmt="d", cmap="YlOrRd", ax=ax, cbar_kws={'label': 'Mahsulotlar Soni'})
        plt.title("13.1. Uzum Market ABC/XYZ Assortiment va Zaxira Matritsasi", pad=15)
        ax.set_ylabel("Daromadlilik Ulushi (ABC: A - 80%, B - 15%, C - 5%)")
        ax.set_xlabel("Talab Barqarorligi (XYZ: X - Stabil, Y - Mavsumiy, Z - Beqaror)")
        plt.tight_layout()
        plt.savefig(f"{self.figures_dir}/13_01_abc_xyz_matrix_heatmap.png", dpi=300)
        plt.close()

        # 2. Top Cross-Selling MBA Rules
        top_rules = mba_rules.head(8).copy()
        if not top_rules.empty:
            labels = [f"[{r['title_A'][:18]}...] + [{r['title_B'][:18]}...]" for _, r in top_rules.iterrows()]
            fig, ax = plt.subplots(figsize=(12, 6))
            bars = ax.barh(labels, top_rules["lift"], color=UZUM_PURPLE, alpha=0.85)
            ax.axvline(1.0, color="red", linestyle="--", label="Mustaqillik chizig'i (Lift=1.0)")
            ax.set_xlabel("Lift Koeffitsienti (Cross-Selling Samaradorligi)")
            for bar in bars:
                val = bar.get_width()
                ax.text(val + 0.05, bar.get_y() + bar.get_height()/2, f"Lift: {val:.2f}", va="center", fontweight="bold")
            plt.title("13.2. Savatchada Eng Ko'p Birga Xarid Qilinadigan Top Tovar Juftliklari (MBA)", pad=15)
            plt.legend()
            plt.tight_layout()
            plt.savefig(f"{self.figures_dir}/13_02_market_basket_top_rules.png", dpi=300)
            plt.close()

    def run(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        print("=== Mahsulotlar ABC/XYZ va Market Basket Tahlili Boshlandi ===")
        df_abc = self.compute_abc_xyz_matrix()
        rules = self.compute_market_basket_analysis()
        self.plot_analytics(df_abc, rules)
        print("=== Mahsulotlar Tahlili Muvaffaqiyatli Yakunlandi ===")
        return df_abc, rules

if __name__ == "__main__":
    pa = UzumProductAnalytics()
    pa.run()
