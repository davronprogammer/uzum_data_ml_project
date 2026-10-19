"""
Uzum Market Domain Analytics Unit Test Suite
============================================
Ushbu test to'plami 11, 12, 13 va 14-bosqichlar (Biznes metrikalari,
RFM segmentatsiyasi, ABC/XYZ matritsasi va Narx elastikligi) hisob-kitoblarini
avtomatlashtirilgan tarzda tekshiradi.
"""

import unittest
from src.analytics.business_metrics import UzumBusinessAnalytics
from src.analytics.customer_rfm import UzumCustomerAnalytics
from src.analytics.product_analytics import UzumProductAnalytics
from src.analytics.pricing_engine import UzumPricingEngine

class TestDomainAnalytics(unittest.TestCase):
    """Domen tahlillari to'g'riligini tekshiruvchi test klassi."""

    def test_business_metrics(self):
        """1. Biznes KPILari va Unit Economics to'g'riligini tekshirish."""
        ba = UzumBusinessAnalytics()
        kpis = ba.compute_kpis()
        self.assertGreater(kpis["gross_gmv_uzs"], 0)
        self.assertLessEqual(kpis["net_gmv_uzs"], kpis["gross_gmv_uzs"])
        self.assertGreater(kpis["marketplace_net_revenue_uzs"], 0)

        ue = ba.compute_unit_economics()
        self.assertGreater(ue["net_contribution_margin_uzs"], 0)
        self.assertGreater(ue["contribution_margin_pct"], 0)

    def test_customer_rfm_segments(self):
        """2. Mijozlar 11 ta RFM segmentiga to'liq ajratilganligini tekshirish."""
        ca = UzumCustomerAnalytics()
        df_rfm = ca.compute_rfm_segments()
        self.assertEqual(len(df_rfm), 3500)
        self.assertFalse(df_rfm["rfm_segment"].isnull().any())
        self.assertIn("Champions", df_rfm["rfm_segment"].values)
        self.assertIn("Loyal Customers", df_rfm["rfm_segment"].values)

    def test_product_abc_xyz_matrix(self):
        """3. Mahsulotlar ABC va XYZ klasslariga to'g'ri bo'linganligini tekshirish."""
        pa = UzumProductAnalytics()
        df_abc = pa.compute_abc_xyz_matrix()
        self.assertEqual(len(df_abc), 2260)
        self.assertTrue(set(df_abc["abc_class"].unique()).issubset({"A", "B", "C"}))
        self.assertTrue(set(df_abc["xyz_class"].unique()).issubset({"X", "Y", "Z"}))

    def test_pricing_elasticity(self):
        """4. Narx elastikligi (PED) va optimal narx tavsiyalari to'g'riligini tekshirish."""
        pe = UzumPricingEngine()
        df_ped = pe.estimate_elasticity_by_category()
        self.assertGreater(len(df_ped), 0)
        self.assertIn("price_elasticity", df_ped.columns)
        self.assertIn("pricing_strategy", df_ped.columns)

if __name__ == "__main__":
    unittest.main()
