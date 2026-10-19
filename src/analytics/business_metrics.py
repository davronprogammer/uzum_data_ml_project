"""
Uzum Market Business Analytics & Unit Economics Module
======================================================
Ushbu modul platforma va do'kon darajasidagi asosiy moliyaviy KPIlarni
(GMV, Net Revenue, Take-Rate, AOV, Bekor qilish/Qaytarish stavkasi)
hamda Unit Economics tahlilini hisoblaydi.
"""

import sqlite3
import numpy as np
import pandas as pd
from typing import Dict, Any

class UzumBusinessAnalytics:
    """Biznes metrikalari va Unit Economics tahlilchisi."""

    def __init__(self, db_path: str = "data/uzum_market.db"):
        self.db_path = db_path
        self._load_data()

    def _load_data(self):
        conn = sqlite3.connect(self.db_path)
        self.df_orders = pd.read_sql_query("SELECT * FROM featured_orders", conn)
        self.df_products = pd.read_sql_query("SELECT * FROM featured_products", conn)
        self.df_order_items = pd.read_sql_query("SELECT * FROM order_items", conn)
        conn.close()

    def compute_kpis(self, take_rate_pct: float = 0.15) -> Dict[str, Any]:
        """Asosiy e-commerce boshqaruv ko'rsatkichlarini hisoblash."""
        total_orders = len(self.df_orders)
        delivered_orders = self.df_orders[self.df_orders["status"] == "Delivered"]
        cancelled_orders = self.df_orders[self.df_orders["status"] == "Cancelled"]
        returned_orders = self.df_orders[self.df_orders["status"] == "Returned"]

        gross_gmv = self.df_orders["total_amount"].sum()
        net_gmv = delivered_orders["total_amount"].sum()

        aov_gross = gross_gmv / total_orders if total_orders > 0 else 0
        aov_net = net_gmv / len(delivered_orders) if len(delivered_orders) > 0 else 0

        # Marketplace komissiyasi (Take-rate tushumi)
        take_rate_revenue = net_gmv * take_rate_pct

        # Bekor qilish va qaytarish stavkalari
        cancellation_rate = (len(cancelled_orders) / total_orders) * 100
        return_rate = (len(returned_orders) / total_orders) * 100

        # Pareto / Konsentratsiya tahlili (Kategoriyalar bo'yicha)
        cat_gmv = self.df_products.groupby("category_id")["orders_count"].sum().sort_values(ascending=False)
        top_20_pct_count = max(1, int(len(cat_gmv) * 0.20))
        top_20_share = (cat_gmv.iloc[:top_20_pct_count].sum() / cat_gmv.sum()) * 100 if cat_gmv.sum() > 0 else 0

        return {
            "total_orders_count": total_orders,
            "delivered_orders_count": len(delivered_orders),
            "gross_gmv_uzs": int(gross_gmv),
            "net_gmv_uzs": int(net_gmv),
            "aov_gross_uzs": int(aov_gross),
            "aov_net_uzs": int(aov_net),
            "marketplace_take_rate_pct": take_rate_pct * 100,
            "marketplace_net_revenue_uzs": int(take_rate_revenue),
            "cancellation_rate_pct": round(cancellation_rate, 2),
            "return_rate_pct": round(return_rate, 2),
            "top_20_categories_volume_share_pct": round(top_20_share, 2),
        }

    def compute_unit_economics(
        self,
        take_rate_pct: float = 0.15,
        payment_gateway_fee_pct: float = 0.015,
        avg_fulfillment_cost_uzs: int = 15000
    ) -> Dict[str, Any]:
        """
        1 ta buyurtmaning Unit Economics taqsimoti:
        - O'rtacha buyurtma (AOV)
        - Marketplace komissiyasi (Revenue)
        - To'lov tizimlari xarajati (Acquiring fee ~1.5%)
        - Logistika va PVZ xarajati (Fulfillment cost)
        - Sof operatsion foyda (Contribution Margin)
        """
        kpis = self.compute_kpis(take_rate_pct)
        aov = kpis["aov_net_uzs"]

        revenue_per_order = aov * take_rate_pct
        payment_fee = aov * payment_gateway_fee_pct
        logistics_cost = avg_fulfillment_cost_uzs
        net_contribution_margin = revenue_per_order - payment_fee - logistics_cost
        cm_margin_pct = (net_contribution_margin / revenue_per_order) * 100 if revenue_per_order > 0 else 0

        return {
            "aov_uzs": aov,
            "gross_commission_revenue_uzs": int(revenue_per_order),
            "payment_processing_fee_uzs": int(payment_fee),
            "fulfillment_logistics_cost_uzs": logistics_cost,
            "net_contribution_margin_uzs": int(net_contribution_margin),
            "contribution_margin_pct": round(cm_margin_pct, 2)
        }

if __name__ == "__main__":
    ba = UzumBusinessAnalytics()
    kpis = ba.compute_kpis()
    ue = ba.compute_unit_economics()
    print("=== BIZNES KPILAR ===")
    for k, v in kpis.items():
        print(f" - {k}: {v}")
    print("\n=== UNIT ECONOMICS ===")
    for k, v in ue.items():
        print(f" - {k}: {v}")
