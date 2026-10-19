# Uzbekistan E-Commerce: Uzum Market Dataset

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

# 2. Place kaggle.json in ~/.kaggle/ (or C:\Users\<User>\.kaggle\kaggle.json)

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
