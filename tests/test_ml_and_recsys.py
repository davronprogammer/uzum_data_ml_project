"""
Uzum Market Machine Learning & Recommendation System Unit Test Suite
====================================================================
Ushbu modul Bestseller klassifikatori va Gibrid Tavsiya Tizimi modellarining
aniqligi, barqarorligi va artefaktlarining yaxlitligini tekshiradi.
"""

import os
import unittest
from src.models.bestseller_classifier import UzumBestsellerClassifier
from src.models.recommender import UzumRecommenderSystem

class TestMLAndRecSys(unittest.TestCase):
    """ML va Tavsiya modellarini tekshiruvchi test klassi."""

    def test_bestseller_classifier(self):
        """1. Bestseller klassifikatori ROC-AUC va saqlangan model artefaktini tekshirish."""
        clf = UzumBestsellerClassifier()
        res = clf.train_and_evaluate()
        self.assertGreater(res["best_auc"], 0.85, "Modelning ROC-AUC aniqligi 0.85 dan past bo'lmasligi kerak!")
        self.assertTrue(os.path.exists(res["artifact_path"]), "Model artefakti fayli topilmadi!")

    def test_hybrid_recommender(self):
        """2. Tavsiya tizimi Top-K tavsiyalar berishi va Cold-Start holatini tekshirish."""
        recsys = UzumRecommenderSystem()
        recsys.build_content_engine()
        recsys.build_collaborative_engine()

        # A. Mavjud tovar uchun tavsiya
        sample_id = recsys.df_products.iloc[0]["product_id"]
        recs = recsys.recommend(sample_id, top_k=5)
        self.assertEqual(len(recs), 5)
        self.assertIn("match_score", recs[0])
        self.assertIn("title", recs[0])

        # B. Noma'lum tovar (Cold-Start fallback)
        unknown_id = 999999999
        fallback_recs = recsys.recommend(unknown_id, top_k=3)
        self.assertEqual(len(fallback_recs), 3)

if __name__ == "__main__":
    unittest.main()
