"""
Uzum Market Time Series & Forecasting Unit Test Suite
=====================================================
Ushbu modul vaqtli qatorlar dekompozitsiyasi va talabni bashorat qilish
(Forecasting) modellarining hisoblash to'g'riligini tekshiradi.
"""

import os
import unittest
import pandas as pd
from src.models.forecasting import UzumSalesForecaster

class TestForecasting(unittest.TestCase):
    """Forecasting modellarini tekshiruvchi test klassi."""

    @classmethod
    def setUpClass(cls):
        cls.forecaster = UzumSalesForecaster()

    def test_decomposition_structure(self):
        """1. Dekompozitsiya komponentlari (Trend, Seasonality, Residuals) to'g'riligini tekshirish."""
        df_decomp = self.forecaster.decompose_time_series()
        self.assertIn("trend", df_decomp.columns)
        self.assertIn("seasonal_weekly", df_decomp.columns)
        self.assertIn("residual", df_decomp.columns)
        self.assertFalse(df_decomp["seasonal_weekly"].isnull().any())

    def test_backtest_metrics_and_future_forecast(self):
        """2. Backtesting metrikalari (WAPE, MAPE) va 60 kunlik prognoz mavjudligini tekshirish."""
        metrics, df_future = self.forecaster.train_and_backtest(test_days=15)
        self.assertIn("gbr_wape", metrics)
        self.assertIn("gbr_mape", metrics)
        self.assertGreater(metrics["gbr_wape"], 0.0)
        self.assertLess(metrics["gbr_wape"], 50.0)

        # 60 kunlik kelgusi prognoz qatorlarini tekshirish
        self.assertEqual(len(df_future), 60)
        self.assertIn("forecast_gmv_uzs", df_future.columns)
        self.assertTrue((df_future["forecast_gmv_uzs"] > 0).all())

        # CSV fayl mavjudligi
        csv_path = "data/processed/sales_forecast_60d.csv"
        self.assertTrue(os.path.exists(csv_path))

if __name__ == "__main__":
    unittest.main()
