"""
Unit tests for Stage 22: Kaggle Dataset Package & Showcase Notebook
"""

import json
import unittest
from pathlib import Path
import pandas as pd


class TestKagglePackage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project_root = Path(__file__).resolve().parent.parent
        cls.kaggle_dir = cls.project_root / "data" / "kaggle"
        cls.notebook_path = cls.project_root / "notebooks" / "kaggle_uzum_showcase.ipynb"

    def test_kaggle_metadata_validity(self):
        """Kaggle dataset-metadata.json fayli mavjud va to'g'ri JSON ekanligini tekshirish."""
        meta_file = self.kaggle_dir / "dataset-metadata.json"
        self.assertTrue(meta_file.exists(), "dataset-metadata.json mavjud emas")
        
        with open(meta_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)
            
        self.assertIn("title", metadata)
        self.assertIn("id", metadata)
        self.assertIn("licenses", metadata)
        self.assertIn("resources", metadata)
        self.assertGreaterEqual(len(metadata["resources"]), 5)

    def test_kaggle_csv_integrity(self):
        """Kaggle katalogidagi asosiy CSV fayllar butunligi va satrlar soni."""
        required_csvs = [
            ("products.csv", 2000),
            ("orders.csv", 10000),
            ("order_items.csv", 10000),
            ("customers.csv", 3000),
            ("categories.csv", 10)
        ]
        for filename, min_rows in required_csvs:
            csv_path = self.kaggle_dir / filename
            self.assertTrue(csv_path.exists(), f"{filename} topilmadi")
            df = pd.read_csv(csv_path)
            self.assertGreater(len(df), min_rows, f"{filename} satrlar soni yetarli emas: {len(df)}")

    def test_kaggle_notebook_structure(self):
        """Kaggle showcase notebook to'g'ri JSON strukturasiga egaligini tekshirish."""
        self.assertTrue(self.notebook_path.exists(), "kaggle_uzum_showcase.ipynb mavjud emas")
        with open(self.notebook_path, "r", encoding="utf-8") as f:
            nb = json.load(f)
        self.assertIn("cells", nb)
        self.assertGreaterEqual(len(nb["cells"]), 10, "Notebook kamida 10 ta katakka ega bo'lishi kerak")
        
        # Tekshirish: Markdown va Kod kataklari mavjudmi
        cell_types = {c.get("cell_type") for c in nb["cells"]}
        self.assertIn("markdown", cell_types)
        self.assertIn("code", cell_types)


if __name__ == "__main__":
    unittest.main()
