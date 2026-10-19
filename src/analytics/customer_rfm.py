"""
Uzum Market Advanced Customer RFM Segmentation & Cohort Retention
==================================================================
Ushbu modul mijozlarni Recency, Frequency, Monetary (RFM) modeli bo'yicha
11 ta xalqaro segmentga ajratadi hamda oylik Kohorta Retention (mijozlar
qaytish darajasi) tahlilini amalga oshiradi.
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

class UzumCustomerAnalytics:
    """Mijozlar segmentatsiyasi va kohorta tahlili klassi."""

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
        self.df_customers = pd.read_sql_query("SELECT * FROM featured_customers", conn)
        self.df_orders = pd.read_sql_query("SELECT * FROM featured_orders", conn)
        conn.close()

    def compute_rfm_segments(self) -> pd.DataFrame:
        """Mijozlarni 11 ta klassik RFM segmentiga ajratish."""
        df = self.df_customers.copy()

        # Kvantillar orqali 1-5 ballik shkala
        # Recency: qancha kam kun bo'lsa, ball shuncha yuqori (5 = eng yangi)
        df["r_score"] = pd.qcut(df["recency_days"], q=5, labels=[5, 4, 3, 2, 1]).astype(int)
        
        # Frequency va Monetary: qancha ko'p bo'lsa, ball shuncha yuqori
        # Dublikatlar ko'p bo'lsa rank method='first' bilan qcut qilish
        df["f_score"] = pd.qcut(df["total_orders"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
        df["m_score"] = pd.qcut(df["total_spent"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)

        df["rfm_score"] = df["r_score"].astype(str) + df["f_score"].astype(str) + df["m_score"].astype(str)

        # 11 ta klassik segmentga xaritalash
        def map_rfm_segment(row):
            r, f = row["r_score"], row["f_score"]
            if r in [4, 5] and f in [4, 5]:
                return "Champions"
            elif r in [3, 4, 5] and f in [3, 4]:
                return "Loyal Customers"
            elif r in [4, 5] and f in [2, 3]:
                return "Potential Loyalists"
            elif r in [4, 5] and f == 1:
                return "Recent Customers"
            elif r in [3, 4] and f == 1:
                return "Promising"
            elif r in [2, 3] and f in [2, 3]:
                return "Customers Needing Attention"
            elif r in [2, 3] and f in [1, 2]:
                return "About to Sleep"
            elif r in [1, 2] and f in [2, 3, 4]:
                return "At Risk"
            elif r in [1, 2] and f == 5:
                return "Can't Lose Them"
            elif r in [1, 2] and f in [1, 2]:
                return "Hibernating"
            elif r == 1 and f == 1:
                return "Lost Customers"
            return "Others"

        df["rfm_segment"] = df.apply(map_rfm_segment, axis=1)

        # CSV va Bazasiga saqlash
        csv_path = os.path.join(self.processed_dir, "customer_rfm_segments.csv")
        df.to_csv(csv_path, index=False, encoding="utf-8")

        conn = sqlite3.connect(self.db_path)
        df.to_sql("customer_rfm_segments", conn, if_exists="replace", index=False)
        conn.close()

        return df

    def compute_cohort_retention(self) -> pd.DataFrame:
        """Kohorta oylari bo'yicha mijozlarning qaytish koeffitsientini (Retention) hisoblash."""
        orders = self.df_orders.copy()
        orders["order_dt"] = pd.to_datetime(orders["order_date"])
        orders["order_month"] = orders["order_dt"].dt.to_period("M")

        # Har bir mijozning 1-xarid oyi (Kohorta)
        cohort_group = orders.groupby("customer_id")["order_month"].min().reset_index()
        cohort_group.columns = ["customer_id", "cohort_month"]

        orders = orders.merge(cohort_group, on="customer_id")

        # Kohorta va buyurtma oyi orasidagi masofa (oylar soni)
        orders["cohort_index"] = (orders["order_month"].dt.year - orders["cohort_month"].dt.year) * 12 + \
                                 (orders["order_month"].dt.month - orders["cohort_month"].dt.month)

        cohort_data = orders.groupby(["cohort_month", "cohort_index"])["customer_id"].nunique().reset_index()
        cohort_pivot = cohort_data.pivot(index="cohort_month", columns="cohort_index", values="customer_id")

        cohort_sizes = cohort_pivot.iloc[:, 0]
        retention_matrix = cohort_pivot.divide(cohort_sizes, axis=0) * 100

        # CSV saqlash
        csv_path = os.path.join(self.processed_dir, "cohort_retention_matrix.csv")
        retention_matrix.to_csv(csv_path, encoding="utf-8")

        return retention_matrix

    def plot_analytics(self, df_rfm: pd.DataFrame, retention_matrix: pd.DataFrame):
        """RFM va Kohorta vizual tasvirlarini saqlash."""
        # 1. RFM Segmentlar Bar Chart
        seg_counts = df_rfm["rfm_segment"].value_counts().sort_values(ascending=True)
        fig, ax = plt.subplots(figsize=(12, 7))
        bars = ax.barh(seg_counts.index, seg_counts.values, color=UZUM_PURPLE, alpha=0.85)
        ax.set_xlabel("Mijozlar Soni")
        for bar in bars:
            val = bar.get_width()
            pct = (val / len(df_rfm)) * 100
            ax.text(val + 10, bar.get_y() + bar.get_height()/2, f"{val} ({pct:.1f}%)", va="center", fontweight="bold")
        plt.title("12.1. Uzum Market Mijozlarining 11 Ta RFM Segmenti Taqsimoti", pad=15)
        plt.tight_layout()
        plt.savefig(f"{self.figures_dir}/12_01_rfm_segments_distribution.png", dpi=300)
        plt.close()

        # 2. Kohorta Heatmap
        fig, ax = plt.subplots(figsize=(14, 8))
        sns.heatmap(retention_matrix, annot=True, fmt=".1f", cmap="Blues", vmin=0, vmax=100, ax=ax,
                    cbar_kws={'label': 'Qayta Xarid Ulushi (%)'})
        plt.title("12.2. Uzum Market Oylik Kohorta Retention Matritsasi (Mijozlar Sodiqligi)", pad=15)
        ax.set_ylabel("Ro'yxatdan O'tgan Kohorta Oyi")
        ax.set_xlabel("O'tgan Oylar Soni (Cohort Period)")
        plt.tight_layout()
        plt.savefig(f"{self.figures_dir}/12_02_cohort_retention_heatmap.png", dpi=300)
        plt.close()

    def run(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        print("=== Mijozlar RFM va Kohorta Tahlili Boshlandi ===")
        df_rfm = self.compute_rfm_segments()
        retention = self.compute_cohort_retention()
        self.plot_analytics(df_rfm, retention)
        print("=== Mijozlar Tahlili Muvaffaqiyatli Yakunlandi ===")
        return df_rfm, retention

if __name__ == "__main__":
    ca = UzumCustomerAnalytics()
    ca.run()
