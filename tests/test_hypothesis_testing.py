"""
Uzum Market Hypothesis Testing Unit Test Suite
==============================================
Ushbu modul statistik gipotezalar sinovi natijalari, p-value va metrikalar
to'g'ri hisoblanganligini tekshiradi.
"""

import unittest
from src.analytics.hypothesis_testing import UzumHypothesisTester

class TestHypothesisTesting(unittest.TestCase):
    """Statistik gipotezalarni tekshiruvchi test klassi."""

    @classmethod
    def setUpClass(cls):
        cls.tester = UzumHypothesisTester()

    def test_hypothesis_1_installment_aov(self):
        """1. Uzum Nasiya AOV testi va Cohen's d mavjudligini tekshirish."""
        res = self.tester.test_hypothesis_1_installment_aov()
        self.assertIn("mann_whitney_p_value", res)
        self.assertIn("cohens_d_effect_size", res)
        self.assertLessEqual(res["mann_whitney_p_value"], 0.05)
        self.assertGreater(res["uplift_pct"], 0)

    def test_hypothesis_2_discount_velocity(self):
        """2. Chegirmalar va sotuv tezligi testini tekshirish."""
        res = self.tester.test_hypothesis_2_discount_velocity()
        self.assertIn("p_value", res)
        self.assertIn("uplift_ratio", res)
        self.assertGreater(res["uplift_ratio"], 1.0)

    def test_hypothesis_3_region_payment_independence(self):
        """3. Chi-Square testi va Cramér's V mavjudligini tekshirish."""
        res = self.tester.test_hypothesis_3_region_payment_independence()
        self.assertIn("chi2_statistic", res)
        self.assertIn("cramers_v_association", res)
        self.assertGreaterEqual(res["cramers_v_association"], 0.0)
        self.assertLessEqual(res["cramers_v_association"], 1.0)

    def test_hypothesis_4_rating_sales_correlation(self):
        """4. Spearman va Kendall korrelyatsiyasi [-1, 1] oralig'ida ekanligini tekshirish."""
        res = self.tester.test_hypothesis_4_rating_sales_correlation()
        self.assertIn("spearman_rho", res)
        self.assertTrue(-1.0 <= res["spearman_rho"] <= 1.0)
        self.assertTrue(-1.0 <= res["kendall_tau"] <= 1.0)

if __name__ == "__main__":
    unittest.main()
