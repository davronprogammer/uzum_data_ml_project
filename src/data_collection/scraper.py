"""
Uzum Market Real-time Scraper & Ingestion Engine
================================================
Ushbu modul Uzum Market platformasidan mahsulotlar katalogi, narxlar,
chegirmalar, reytinglar va nasiya (muddatli to'lov) ma'lumotlarini
asinxron/barqaror usulda yig'adi va data/raw/ papkasiga xom holatda saqlaydi.
"""

import json
import logging
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("UzumScraper")

class UzumScraper:
    """Uzum Market ochiq API'laridan ma'lumot yig'ish klassi."""

    def __init__(self, raw_output_path: str = "data/raw/uzum_catalog_raw.json"):
        self.raw_output_path = raw_output_path
        self.base_url = "https://api.uzum.uz/api"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "uz-UZ,uz;q=0.9,ru;q=0.8",
            "Connection": "keep-alive"
        }

    def fetch_mobile_main_feed(self, timeout: int = 40, retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        Uzum Market mobil oqimidan barcha dolzarb aksiyalar,
        toifalar va mahsulotlar to'plamini yuklab oladi.
        """
        url = f"{self.base_url}/main/mobile"
        logger.info(f"So'rov yuborilmoqda: {url} (Timeout: {timeout}s)...")

        for attempt in range(1, retries + 1):
            try:
                req = urllib.request.Request(url, headers=self.headers)
                start_time = time.time()
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    duration = time.time() - start_time
                    logger.info(f"Muvaffaqiyatli yuklandi ({response.status}) {duration:.2f} soniyada.")
                    raw_bytes = response.read()
                    data = json.loads(raw_bytes.decode("utf-8"))
                    return data
            except (urllib.error.URLError, TimeoutError, Exception) as e:
                logger.warning(f"Urinish {attempt}/{retries} muvaffaqiyatsiz bo'ldi: {e}")
                if attempt < retries:
                    sleep_time = attempt * 3
                    logger.info(f"{sleep_time} soniya kutilmoqda (Exponential backoff)...")
                    time.sleep(sleep_time)

        logger.error(f"{retries} ta urinishdan so'ng ma'lumotni yuklab bo'lmadi.")
        return None

    def parse_products_from_feed(self, raw_feed: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Xom JSON oqimidan Data Dictionary standartimizga mos
        bo'lgan toza mahsulotlar lug'atini ajratib oladi.
        """
        payload = raw_feed.get("payload", {})
        offers = payload.get("offers", [])
        product_groups = payload.get("productGroups", [])
        
        extracted_products: Dict[int, Dict[str, Any]] = {}
        crawl_time = datetime.now(timezone.utc).isoformat()

        # Barcha offer va guruhlarni aylanib chiqamiz
        all_containers = offers + product_groups
        logger.info(f"{len(all_containers)} ta taklif va toifalar bloki tahlil qilinmoqda...")

        for container in all_containers:
            category_title = container.get("title", "Umumiy")
            category_id = container.get("categoryId")
            
            # Mahsulotlar ro'yxatini topish
            products = container.get("productList", []) or container.get("products", [])
            for p in products:
                prod_id = p.get("productId")
                if not prod_id:
                    continue

                # Agar avval ko'rilmagan bo'lsa, lug'atga qo'shamiz
                if prod_id not in extracted_products:
                    # Nasiya / Installment narxini badge'dan ajratish
                    installment_price = 0
                    has_installment = False
                    for b in p.get("badges", []) or []:
                        text = b.get("text", "")
                        if "oyiga" in text.lower() or "so'm" in text.lower():
                            has_installment = True
                            # Raqamlarni ajratib olish
                            clean_num = "".join(ch for ch in text if ch.isdigit())
                            if clean_num:
                                installment_price = int(clean_num)
                                break

                    sell_price = p.get("sellPrice") or p.get("minSellPrice") or 0
                    full_price = p.get("fullPrice") or p.get("minFullPrice") or sell_price

                    # Chegirma hisoblash
                    discount_pct = 0.0
                    if full_price > sell_price and full_price > 0:
                        discount_pct = round(((full_price - sell_price) / full_price) * 100, 2)

                    extracted_products[prod_id] = {
                        "product_id": prod_id,
                        "title": p.get("title", "").strip(),
                        "category_id": p.get("categoryId") or category_id,
                        "category_name": category_title,
                        "price_current": sell_price,
                        "price_original": full_price,
                        "discount_percentage": discount_pct,
                        "monthly_installment": installment_price,
                        "has_installment": has_installment,
                        "rating": float(p.get("rating", 0.0) or 0.0),
                        "reviews_count": int(p.get("reviewsQuantity", 0) or 0),
                        "orders_count": int(p.get("ordersQuantity", 0) or 0),
                        "is_eco": bool(p.get("isEco", False)),
                        "is_adult": bool(p.get("isAdultCategory", False)),
                        "image_url": p.get("image") or p.get("compressedImage"),
                        "delivery_time_days": 1,  # Uzum standarti: 1 kun
                        "delivery_type": "PVZ",
                        "crawled_at": crawl_time
                    }

        result_list = list(extracted_products.values())
        logger.info(f"Jami {len(result_list)} ta unikal tovar ma'lumotlari muvaffaqiyatli ajratildi.")
        return result_list

    def save_raw_data(self, data: List[Dict[str, Any]]) -> str:
        """Xom ma'lumotlarni data/raw/ katalogiga saqlaydi."""
        os.makedirs(os.path.dirname(self.raw_output_path), exist_ok=True)
        with open(self.raw_output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Xom ma'lumot saqlandi: {self.raw_output_path} ({len(data)} yozuv)")
        return self.raw_output_path

    def run(self) -> List[Dict[str, Any]]:
        """Butun skreper pipelineni boshqaradi."""
        logger.info("=== Uzum Market Scraper Pipeline Boshlandi ===")
        raw_feed = self.fetch_mobile_main_feed()
        if not raw_feed:
            raise RuntimeError("Uzum Market API'dan ma'lumot olib bo'lmadi.")
        
        products = self.parse_products_from_feed(raw_feed)
        self.save_raw_data(products)
        logger.info("=== Scraper Pipeline Muvaffaqiyatli Yakunlandi ===")
        return products

if __name__ == "__main__":
    scraper = UzumScraper()
    scraper.run()
