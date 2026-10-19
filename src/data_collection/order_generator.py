"""
Uzum Market Realistic Transaction & Order History Generator
============================================================
Ushbu modul data/raw/uzum_catalog_raw.json faylidagi haqiqiy skreper qilingan
2,260+ ta tovarlar asosida tranzaksiyalar (buyurtmalar savatchasi, xaridorlar,
to'lov turlari, O'zbekiston viloyatlari va vaqt sikllari) tarixini modellashtiradi.

Bu ma'lumotlar quyidagi bo'limlar uchun zarur poydevor bo'ladi:
- Mijozlar tahlili (RFM Segmentation, Cohorts)
- Bozor savatchasi tahlili (Market Basket Analysis - Apriori)
- Geografik tahlil (Viloyatlar va PVZ topshirish punktlari)
- Vaqtli qatorlar (Time Series & Forecasting: Ramazon, Navro'z, 11.11)
"""

import json
import logging
import math
import os
import random
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("OrderGenerator")

# O'zbekiston viloyatlari va ularning e-commerce faollik ulushi (vaznlari)
REGIONS_DISTRIBUTION = [
    ("Toshkent shahri", 0.38),
    ("Toshkent viloyati", 0.12),
    ("Samarqand", 0.10),
    ("Farg'ona", 0.08),
    ("Andijon", 0.07),
    ("Namangan", 0.06),
    ("Buxoro", 0.05),
    ("Qashqadaryo", 0.04),
    ("Xorazm", 0.03),
    ("Surxondaryo", 0.025),
    ("Navoiy", 0.02),
    ("Jizzax", 0.015),
    ("Qoraqalpog'iston", 0.01),
]

PAYMENT_METHODS = [
    ("Uzum Pay", 0.35),
    ("Uzum Nasiya (Muddatli)", 0.25),
    ("Click", 0.20),
    ("Payme", 0.12),
    ("Naqd / Karta (PVZda)", 0.08),
]

class UzumOrderGenerator:
    """Haqiqiy tovarlar asosida buyurtmalar tarixini modellashtiruvchi klass."""

    def __init__(
        self,
        catalog_path: str = "data/raw/uzum_catalog_raw.json",
        output_orders_path: str = "data/raw/uzum_orders_raw.json",
        seed: int = 42
    ):
        self.catalog_path = catalog_path
        self.output_orders_path = output_orders_path
        self.seed = seed
        random.seed(seed)

    def load_catalog(self) -> List[Dict[str, Any]]:
        """Haqiqiy skreper qilingan tovarlarni o'qish."""
        if not os.path.exists(self.catalog_path):
            raise FileNotFoundError(f"Katalog fayli topilmadi: {self.catalog_path}")
        with open(self.catalog_path, "r", encoding="utf-8") as f:
            catalog = json.load(f)
        logger.info(f"{len(catalog)} ta haqiqiy tovar katalogdan o'qildi.")
        return catalog

    def _get_seasonal_multiplier(self, dt: datetime) -> float:
        """
        O'zbekiston e-commerce mavsumiylik multiplikatori:
        - 11.11 (Katta sotuvlar): 2.5x
        - Yangi yil (15-31 dekabr): 2.0x
        - 8-mart: 1.6x
        - Navro'z (15-25 mart): 1.5x
        - Maktab bozori (15-avgust - 5-sentyabr): 1.7x
        - Haftaning juma-yakshanba kunlari: 1.2x
        """
        mult = 1.0
        # Hafta kunlari
        if dt.weekday() in (4, 5, 6): # Juma, Shanba, Yakshanba
            mult *= 1.2
        
        # 11.11 aksiyasi
        if dt.month == 11 and 9 <= dt.day <= 13:
            mult *= 2.6
        # Dekabr bayramlari
        elif dt.month == 12 and dt.day >= 15:
            mult *= 2.1
        # 8-mart
        elif dt.month == 3 and 1 <= dt.day <= 8:
            mult *= 1.6
        # Navro'z
        elif dt.month == 3 and 15 <= dt.day <= 22:
            mult *= 1.5
        # Maktab bozori
        elif (dt.month == 8 and dt.day >= 15) or (dt.month == 9 and dt.day <= 5):
            mult *= 1.7

        return mult

    def generate_orders(
        self,
        num_customers: int = 3500,
        days_history: int = 365,
        target_orders_count: int = 25000
    ) -> List[Dict[str, Any]]:
        """
        Realistik xaridorlar kohortasi va tranzaksiyalarini generatsiya qilish.
        """
        catalog = self.load_catalog()
        products_by_category: Dict[str, List[Dict[str, Any]]] = {}
        for p in catalog:
            cat = p.get("category_name", "Umumiy")
            products_by_category.setdefault(cat, []).append(p)

        # 1. Mijozlar profilini shakllantirish
        logger.info(f"{num_customers} ta mijoz profillari yaratilmoqda...")
        customers = []
        regions, region_weights = zip(*REGIONS_DISTRIBUTION)
        
        for cid in range(1, num_customers + 1):
            customer_region = random.choices(regions, weights=region_weights)[0]
            # Mijozning qachon ro'yxatdan o'tganligi
            join_day_offset = random.randint(0, days_history - 30)
            # Mijoz faolligi (Pareto printsipi: 20% mijozlar 80% buyurtmalarni beradi)
            activity_level = random.choices(
                ["vip", "regular", "occasional", "one_time"],
                weights=[0.05, 0.20, 0.35, 0.40]
            )[0]
            customers.append({
                "customer_id": f"CUST_{cid:05d}",
                "region": customer_region,
                "join_offset": join_day_offset,
                "activity": activity_level
            })

        # 2. Buyurtmalarni generatsiya qilish
        logger.info(f"O'tgan {days_history} kunlik tranzaksiyalar modellashtirilmoqda...")
        orders = []
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days_history)

        order_id_counter = 1000001
        pay_methods, pay_weights = zip(*PAYMENT_METHODS)

        # Har bir mijoz uchun o'z faolligiga mos buyurtmalar yaratish
        for cust in customers:
            if cust["activity"] == "vip":
                order_freq = random.randint(12, 35)
            elif cust["activity"] == "regular":
                order_freq = random.randint(5, 14)
            elif cust["activity"] == "occasional":
                order_freq = random.randint(2, 5)
            else:
                order_freq = 1

            cust_start = start_date + timedelta(days=cust["join_offset"])
            days_active = max(1, (end_date - cust_start).days)

            for _ in range(order_freq):
                day_offset = random.randint(0, days_active - 1)
                order_dt = cust_start + timedelta(
                    days=day_offset,
                    hours=random.randint(8, 23),
                    minutes=random.randint(0, 59)
                )

                # Savatchadagi tovarlar soni (Basket size)
                # Odatda 1-4 xil tovar
                basket_items_count = random.choices([1, 2, 3, 4, 5], weights=[0.55, 0.25, 0.12, 0.05, 0.03])[0]
                
                # Asosiy toifani tanlaymiz (bir toifadan tovarlar birga olinishi ehtimoli yuqori)
                main_cat = random.choice(list(products_by_category.keys()))
                cat_products = products_by_category[main_cat]
                
                selected_products = random.sample(cat_products, min(basket_items_count, len(cat_products)))
                
                basket_items = []
                total_order_amount = 0

                for prod in selected_products:
                    qty = random.choices([1, 2, 3], weights=[0.85, 0.12, 0.03])[0]
                    item_price = prod["price_current"]
                    line_total = item_price * qty
                    total_order_amount += line_total
                    basket_items.append({
                        "product_id": prod["product_id"],
                        "title": prod["title"],
                        "category_name": prod["category_name"],
                        "unit_price": item_price,
                        "quantity": qty,
                        "line_total": line_total
                    })

                # To'lov turi: agar narx 1 000 000 so'mdan oshsa, Nasiya ulushi oshadi
                if total_order_amount > 1_000_000:
                    cust_payment = random.choices(
                        pay_methods,
                        weights=[0.20, 0.50, 0.15, 0.10, 0.05]
                    )[0]
                else:
                    cust_payment = random.choices(pay_methods, weights=pay_weights)[0]

                # Yetkazib berish turi
                delivery_method = random.choices(["PVZ (Topshirish punkti)", "Kuryer orqali"], weights=[0.88, 0.12])[0]
                
                # Status
                status = random.choices(
                    ["Delivered", "Cancelled", "Returned"],
                    weights=[0.92, 0.05, 0.03]
                )[0]

                orders.append({
                    "order_id": f"ORD_{order_id_counter}",
                    "customer_id": cust["customer_id"],
                    "order_date": order_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "region": cust["region"],
                    "delivery_type": delivery_method,
                    "payment_method": cust_payment,
                    "status": status,
                    "items_count": len(basket_items),
                    "total_amount": total_order_amount,
                    "items": basket_items
                })
                order_id_counter += 1

        # Sana bo'yicha saralash
        orders.sort(key=lambda x: x["order_date"])
        logger.info(f"Jami {len(orders)} ta realistik buyurtma tranzaksiyalari yaratildi.")
        
        # Diskka saqlash
        os.makedirs(os.path.dirname(self.output_orders_path), exist_ok=True)
        with open(self.output_orders_path, "w", encoding="utf-8") as f:
            json.dump(orders, f, ensure_ascii=False, indent=2)
        logger.info(f"Buyurtmalar muvaffaqiyatli saqlandi: {self.output_orders_path}")
        return orders

if __name__ == "__main__":
    generator = UzumOrderGenerator()
    generator.generate_orders(num_customers=3500, days_history=365)
