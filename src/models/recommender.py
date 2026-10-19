"""
Uzum Market Hybrid Recommendation System
=========================================
Ushbu modul Uzum Market foydalanuvchilari uchun gibrid tavsiya tizimini
amalga oshiradi:
1. Content-Based Filtering: TF-IDF va Cosine Similarity orqali matnli
   va toifaviy o'xshash tovarlarni topish ("O'xshash Mahsulotlar").
2. Collaborative Basket Filtering: Tranzaksiyalar savatchasi orqali
   birga eng ko'p olinadigan tovarlarni topish ("Buni olganlar buni ham xarid qilishdi").
3. Hybrid Blending: Ikkala signalni birlashtirish va yangi tovarlar uchun
   "Cold Start" muammosini hal qilish.
"""

import os
import pickle
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

UZUM_PURPLE = "#7000FF"
ACCENT_GREEN = "#00C853"
ACCENT_ORANGE = "#FF6D00"
ACCENT_BLUE = "#2979FF"

class UzumRecommenderSystem:
    """Gibrid tavsiya tizimi klassi."""

    def __init__(
        self,
        db_path: str = "data/uzum_market.db",
        models_dir: str = "models",
        figures_dir: str = "reports/figures"
    ):
        self.db_path = db_path
        self.models_dir = models_dir
        self.figures_dir = figures_dir
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.figures_dir, exist_ok=True)
        self._load_data()

    def _load_data(self):
        conn = sqlite3.connect(self.db_path)
        self.df_products = pd.read_sql_query("""
            SELECT p.*, c.category_name 
            FROM featured_products p 
            LEFT JOIN categories c ON p.category_id = c.category_id
        """, conn)
        self.df_order_items = pd.read_sql_query("SELECT * FROM order_items", conn)
        conn.close()

    def build_content_engine(self):
        """TF-IDF asosida matnli o'xshashlik matritsasini qurish."""
        # Tovar nomi va toifasini birlashtirish
        corpus = self.df_products["title"].fillna("") + " " + self.df_products["category_name"].fillna("")
        
        self.tfidf = TfidfVectorizer(max_features=1500, stop_words="english", ngram_range=(1, 2))
        tfidf_matrix = self.tfidf.fit_transform(corpus)

        self.cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        self.product_indices = pd.Series(self.df_products.index, index=self.df_products["product_id"]).drop_duplicates()

    def build_collaborative_engine(self):
        """Savatchalar birikmasi (Co-occurrence) matritsasini qurish."""
        # Har bir savatdagi tovarlar ro'yxati
        basket_counts = self.df_order_items.groupby("order_id")["product_id"].count()
        multi_baskets = basket_counts[basket_counts > 1].index
        multi_items = self.df_order_items[self.df_order_items["order_id"].isin(multi_baskets)]

        # Juftliklar
        merged = multi_items.merge(multi_items, on="order_id", suffixes=("_A", "_B"))
        merged = merged[merged["product_id_A"] != merged["product_id_B"]]

        co_matrix = merged.groupby(["product_id_A", "product_id_B"])["order_id"].count().reset_index()
        co_matrix.columns = ["product_id_A", "product_id_B", "co_count"]
        self.co_matrix = co_matrix

    def recommend(
        self,
        product_id: int,
        top_k: int = 5,
        alpha: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Gibrid tavsiyalar generatsiyasi:
        Score = alpha * Content_Score + (1 - alpha) * Collaborative_Score
        """
        if product_id not in self.product_indices:
            # Agar yangi tovar bo'lsa, eng ommabop hit tovarlarni qaytarish (Fallback)
            top_pop = self.df_products.sort_values("orders_count", ascending=False).head(top_k)
            return top_pop[["product_id", "title", "price_current", "bayesian_rating"]].to_dict(orient="records")

        idx = self.product_indices[product_id]
        
        # 1. Content sim ballari
        content_scores = self.cosine_sim[idx].copy()
        
        # 2. Collaborative birgalikda olinganlar ballari
        collab_scores = np.zeros(len(self.df_products))
        related_baskets = self.co_matrix[self.co_matrix["product_id_A"] == product_id]
        
        if not related_baskets.empty:
            max_co = related_baskets["co_count"].max()
            for _, r in related_baskets.iterrows():
                target_pid = r["product_id_B"]
                if target_pid in self.product_indices:
                    t_idx = self.product_indices[target_pid]
                    collab_scores[t_idx] = r["co_count"] / max_co if max_co > 0 else 0

        # Gibrid vaznli ball
        hybrid_scores = alpha * content_scores + (1 - alpha) * collab_scores
        hybrid_scores[idx] = -1.0  # O'zini o'ziga tavsiya qilmaslik

        # Top-K indekslarini tanlash
        top_indices = np.argsort(hybrid_scores)[::-1][:top_k]
        recommended_products = self.df_products.iloc[top_indices].copy()
        recommended_products["match_score"] = hybrid_scores[top_indices].round(3)

        return recommended_products[[
            "product_id", "title", "price_current", "bayesian_rating", "category_name", "match_score"
        ]].to_dict(orient="records")

    def plot_recommendation_showcase(self):
        """Tavsiya tizimi ko'rgazmali grafik hisoboti."""
        # Namunaviy tovar uchun tavsiya olish
        sample_prod = self.df_products.sort_values("orders_count", ascending=False).iloc[5]
        sample_id = sample_prod["product_id"]
        sample_title = sample_prod["title"]

        recs = self.recommend(sample_id, top_k=5)
        rec_df = pd.DataFrame(recs)

        fig, ax = plt.subplots(figsize=(12, 6))
        labels = [f"[{r['category_name'][:12]}] {r['title'][:25]}..." for _, r in rec_df.iterrows()]
        bars = ax.barh(labels, rec_df["match_score"], color=UZUM_PURPLE, alpha=0.85)
        ax.set_xlabel("Gibrid Moslik Koeffitsienti (Match Score: 0..1)")
        for bar in bars:
            val = bar.get_width()
            ax.text(val + 0.01, bar.get_y() + bar.get_height()/2, f"Moslik: {val:.2f}", va="center", fontweight="bold")

        plt.title(f"18.1. '{sample_title[:35]}...' Uchun Gibrid AI Tavsiyalar Natijasi", pad=15)
        plt.tight_layout()
        plt.savefig(f"{self.figures_dir}/18_01_recommendation_showcase.png", dpi=300)
        plt.close()

    def run(self) -> str:
        print("=== Gibrid Tavsiya Tizimi O'qitilmoqda ===")
        self.build_content_engine()
        self.build_collaborative_engine()
        self.plot_recommendation_showcase()

        # Model holatini saqlash
        artifact_path = os.path.join(self.models_dir, "recommender_system.pkl")
        with open(artifact_path, "wb") as f:
            pickle.dump({
                "tfidf": self.tfidf,
                "cosine_sim": self.cosine_sim,
                "co_matrix": self.co_matrix,
                "product_indices": self.product_indices
            }, f)
        print(f"=== Tavsiya Modeli Muvaffaqiyatli Saqlandi: {artifact_path} ===")
        return artifact_path

if __name__ == "__main__":
    recsys = UzumRecommenderSystem()
    recsys.run()
    # Test tavsiya
    sample_id = recsys.df_products.iloc[0]["product_id"]
    test_recs = recsys.recommend(sample_id, top_k=3)
    print("\n--- TEST TAVSIYALAR ---")
    for r in test_recs:
        print(f" - {r['title']} | Narx: {r['price_current']} UZS | Score: {r['match_score']}")
