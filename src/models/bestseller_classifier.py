"""
Uzum Market Bestseller Success Classifier & Feature Explainability Engine
========================================================================
Ushbu modul do'konga yangi kiritilayotgan tovarning "Hit / Bestseller" bo'lish
ehtimolini oldindan klassifikatsiya qiladi va qaysi omillar (Nasiya, chegirma,
narx nisbati, reyting) muvaffaqiyatga ko'proq ta'sir qilishini aniqlaydi.
"""

import os
import pickle
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any, Tuple
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve, precision_score, recall_score, f1_score, confusion_matrix

UZUM_PURPLE = "#7000FF"
ACCENT_GREEN = "#00C853"
ACCENT_ORANGE = "#FF6D00"
ACCENT_BLUE = "#2979FF"
DARK_SLATE = "#1F1F26"

class UzumBestsellerClassifier:
    """Tovar muvaffaqiyatini bashorat qiluvchi ML modeli klassi."""

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
        self.df_products = pd.read_sql_query("SELECT * FROM featured_products", conn)
        conn.close()

    def prepare_dataset(self) -> Tuple[pd.DataFrame, pd.Series, list]:
        """ML modeli uchun xususiyatlar (X) va nishon belgisini (y) shakllantirish."""
        df = self.df_products.copy()

        # Nishon belgisi: Agar tovar buyurtmalar soni bo'yicha 75-persentildan yuqori bo'lsa -> Bestseller (1)
        threshold = df["orders_count"].quantile(0.75)
        df["is_bestseller"] = (df["orders_count"] >= threshold).astype(int)

        # Kategoriya chastota kodlash (Frequency encoding)
        cat_freq = df["category_id"].value_counts(normalize=True).to_dict()
        df["category_freq"] = df["category_id"].map(cat_freq)

        # One-Hot Encoding: price_segment va discount_tier
        df_encoded = pd.get_dummies(df, columns=["price_segment", "discount_tier"], drop_first=True)

        feature_cols = [
            "price_current",
            "price_relative_ratio",
            "discount_percentage",
            "has_installment",
            "monthly_installment",
            "bayesian_rating",
            "reviews_count",
            "delivery_time_days",
            "category_freq"
        ]
        # One-hot ustunlarini qo'shish
        dummy_cols = [c for c in df_encoded.columns if c.startswith("price_segment_") or c.startswith("discount_tier_")]
        feature_cols.extend(dummy_cols)

        X = df_encoded[feature_cols].fillna(0)
        y = df["is_bestseller"]

        return X, y, feature_cols

    def train_and_evaluate(self) -> Dict[str, Any]:
        """Modellarni solishtirish va eng yaxshisini tanlash."""
        X, y, feature_names = self.prepare_dataset()

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y
        )

        models = {
            "Logistic Regression (Baseline)": LogisticRegression(max_iter=1000, random_state=42),
            "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42),
            "Gradient Boosting (GBM)": GradientBoostingClassifier(n_estimators=120, learning_rate=0.08, max_depth=4, random_state=42)
        }

        results = {}
        best_model = None
        best_auc = 0.0
        best_model_name = ""

        plt.figure(figsize=(9, 7))

        for name, clf in models.items():
            clf.fit(X_train, y_train)
            y_pred_proba = clf.predict_proba(X_test)[:, 1]
            y_pred = clf.predict(X_test)

            auc = roc_auc_score(y_test, y_pred_proba)
            prec = precision_score(y_test, y_pred)
            rec = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)

            fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
            plt.plot(fpr, tpr, linewidth=2, label=f"{name} (AUC = {auc:.3f})")

            results[name] = {
                "ROC_AUC": round(auc, 4),
                "Precision": round(prec, 4),
                "Recall": round(rec, 4),
                "F1_Score": round(f1, 4)
            }

            if auc > best_auc:
                best_auc = auc
                best_model = clf
                best_model_name = name

        # ROC Curve vizualizatsiyasi
        plt.plot([0, 1], [0, 1], "k--", alpha=0.6, label="Tasodifiy taxmin (AUC = 0.500)")
        plt.xlabel("False Positive Rate (FPR)")
        plt.ylabel("True Positive Rate (TPR)")
        plt.title("17.1. Bestseller Klassifikatorlari: ROC-AUC Egri Chiziqlari Taqqoslovi", pad=15)
        plt.legend(loc="lower right")
        plt.tight_layout()
        plt.savefig(f"{self.figures_dir}/17_01_bestseller_model_roc_auc.png", dpi=300)
        plt.close()

        # Feature Importance (Eng muhim omillar)
        if hasattr(best_model, "feature_importances_"):
            importances = best_model.feature_importances_
        elif hasattr(best_model, "coef_"):
            importances = np.abs(best_model.coef_[0])
            importances = importances / np.sum(importances)
        else:
            importances = None

        if importances is not None:
            feat_imp = pd.Series(importances, index=feature_names).sort_values(ascending=True)

            fig, ax = plt.subplots(figsize=(10, 7))
            bars = ax.barh(feat_imp.index, feat_imp.values, color=UZUM_PURPLE, alpha=0.85)
            ax.set_xlabel("Nisbiy Muhimlik Darajasi (Feature Importance Score)")
            for bar in bars:
                val = bar.get_width()
                ax.text(val + 0.005, bar.get_y() + bar.get_height()/2, f"{val:.3f}", va="center", fontweight="bold")
            plt.title(f"17.2. Tovarning Bestseller Bo'lishini Beliglovchi Top Omillar ({best_model_name})", pad=15)
            plt.tight_layout()
            plt.savefig(f"{self.figures_dir}/17_02_feature_importance.png", dpi=300)
            plt.close()

        # Modelni saqlash
        model_artifact_path = os.path.join(self.models_dir, "bestseller_classifier.pkl")
        with open(model_artifact_path, "wb") as f:
            pickle.dump({
                "model": best_model,
                "model_name": best_model_name,
                "feature_names": feature_names,
                "metrics": results[best_model_name]
            }, f)

        return {
            "comparison": results,
            "best_model_name": best_model_name,
            "best_auc": best_auc,
            "artifact_path": model_artifact_path
        }

    def run(self) -> Dict[str, Any]:
        print("=== Bestseller Klassifikatori ML O'qitish Boshlandi ===")
        res = self.train_and_evaluate()
        print("=== ML Klassifikator Muvaffaqiyatli Yakunlandi ===")
        return res

if __name__ == "__main__":
    clf = UzumBestsellerClassifier()
    out = clf.run()
    print("\n--- ML MODELLAR TAQQOSLOVI ---")
    for m, met in out["comparison"].items():
        print(f"\n[{m}]")
        for k, v in met.items():
            print(f"  - {k}: {v}")
    print(f"\nEng yaxshi model: {out['best_model_name']} (AUC: {out['best_auc']:.4f})")
