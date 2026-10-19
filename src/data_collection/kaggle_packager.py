"""
Uzum Market: Kaggle Dataset Packager
Tayyorlangan toza ma'lumotlar to'plamini Kaggle platformasi standartlariga
mos ravishda data/kaggle/ katalogiga paketlaydi va dataset-metadata.json yaratadi.
"""

import json
import logging
import shutil
from pathlib import Path
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] KagglePackager: %(message)s")
logger = logging.getLogger(__name__)


def build_kaggle_package(project_root: Path | None = None) -> Path:
    """Kaggle uchun toza CSV fayllar, metadata va README ni tayyorlaydi."""
    if project_root is None:
        project_root = Path(__file__).resolve().parent.parent.parent

    processed_dir = project_root / "data" / "processed"
    kaggle_dir = project_root / "data" / "kaggle"
    kaggle_dir.mkdir(parents=True, exist_ok=True)

    files_map = {
        "clean_products.csv": "products.csv",
        "clean_orders.csv": "orders.csv",
        "clean_order_items.csv": "order_items.csv",
        "clean_customers.csv": "customers.csv",
        "clean_categories.csv": "categories.csv",
        "customer_rfm_segments.csv": "customer_rfm_segments.csv",
        "price_elasticity_by_category.csv": "price_elasticity_by_category.csv",
        "product_abc_xyz_analysis.csv": "product_abc_xyz_analysis.csv",
        "sales_forecast_60d.csv": "sales_forecast_60d.csv",
    }

    copied_files = []
    for src_name, dst_name in files_map.items():
        src_path = processed_dir / src_name
        dst_path = kaggle_dir / dst_name
        if src_path.exists():
            shutil.copy2(src_path, dst_path)
            copied_files.append(dst_name)
            logger.info("Fayl ko'chirildi: %s -> %s", src_name, dst_name)
        else:
            logger.warning("Fayl topilmadi: %s", src_path)

    # Kaggle dataset-metadata.json yaratish
    metadata = {
        "title": "Uzbekistan E-Commerce: Uzum Market Dataset",
        "id": "YOUR_USERNAME/uzum-market-ecommerce-dataset",
        "licenses": [
            {
                "name": "CC0-1.0"
            }
        ],
        "description": (
            "Comprehensive Uzbekistan E-Commerce dataset scraped and modeled from Uzum Market, "
            "the leading national marketplace in Uzbekistan. Includes 2,260 products, 16,917 order "
            "transactions, customer segmentation (RFM), Uzum Nasiya installment data, price elasticity, "
            "and 60-day sales demand forecasting."
        ),
        "keywords": [
            "ecommerce",
            "retail",
            "uzbekistan",
            "market basket analysis",
            "rfm segmentation",
            "demand forecasting",
            "price elasticity",
            "central asia"
        ],
        "resources": [
            {
                "path": "products.csv",
                "description": "2,260 real products scraped from Uzum Market API with prices, reviews, ratings, and Nasiya badges."
            },
            {
                "path": "orders.csv",
                "description": "16,917 customer purchase transactions across 13 regions in Uzbekistan (2025-2026)."
            },
            {
                "path": "order_items.csv",
                "description": "Item-level lines inside orders with unit prices, quantity, and product associations."
            },
            {
                "path": "customers.csv",
                "description": "3,500 customer demographic and regional profile records."
            },
            {
                "path": "categories.csv",
                "description": "Category hierarchy tree from Uzum marketplace."
            },
            {
                "path": "customer_rfm_segments.csv",
                "description": "Engineered RFM scores (Recency, Frequency, Monetary) with 11 distinct customer segments."
            },
            {
                "path": "price_elasticity_by_category.csv",
                "description": "Log-Log econometric price elasticity of demand (PED) by product category."
            },
            {
                "path": "product_abc_xyz_analysis.csv",
                "description": "ABC/XYZ inventory matrix and coefficient of variation."
            },
            {
                "path": "sales_forecast_60d.csv",
                "description": "60-day forward demand forecast generated via Gradient Boosting ML Forecaster."
            }
        ]
    }

    metadata_path = kaggle_dir / "dataset-metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    logger.info("dataset-metadata.json muvaffaqiyatli yaratildi: %s", metadata_path)

    # Kaggle README.md yaratish
    readme_content = """# Uzbekistan E-Commerce: Uzum Market Dataset

## Overview
This dataset contains transactional, product assortment, customer behavior, and price elasticity records from **Uzum Market**, the largest e-commerce platform and national ecosystem in Uzbekistan.

## Contents
1. `products.csv`: 2,260 products with original prices, discount prices, seller ratings, reviews, and badges.
2. `orders.csv`: 16,917 transactions including payment types (`Uzum Nasiya`, `Payme`, `Click`, `Cash`), order status, delivery days, and delivery regions.
3. `order_items.csv`: Detailed line items per basket.
4. `customers.csv`: 3,500 registered marketplace buyers across 13 regions.
5. `categories.csv`: Product category hierarchy.
6. `customer_rfm_segments.csv`: Customer RFM segmentation (Champions, Loyal, At Risk, Hibernating, etc.).
7. `price_elasticity_by_category.csv`: Econometric Price Elasticity of Demand (PED).
8. `product_abc_xyz_analysis.csv`: ABC (revenue contribution) and XYZ (demand volatility) classification.
9. `sales_forecast_60d.csv`: 60-day daily forward sales demand forecast.

## How to Upload to Kaggle via CLI
```bash
# 1. Install Kaggle CLI
pip install kaggle

# 2. Place kaggle.json in ~/.kaggle/ (or C:\\Users\\<User>\\.kaggle\\kaggle.json)

# 3. Edit "id" in dataset-metadata.json with your Kaggle username:
#    "id": "your_username/uzum-market-ecommerce-dataset"

# 4. Upload dataset
kaggle datasets create -p data/kaggle/
```

## Potential Research Questions
- What is the revenue uplift of fintech installments (Uzum Nasiya) compared to direct card payments?
- How does price elasticity vary between essential fast-moving goods and consumer electronics?
- Which product pairings yield the highest cross-sell lift in Market Basket Analysis?
- How to accurately predict 60-day demand surges during weekend shopping cycles?
"""
    readme_path = kaggle_dir / "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    logger.info("Kaggle README.md yaratildi: %s", readme_path)

    return kaggle_dir


if __name__ == "__main__":
    build_kaggle_package()
