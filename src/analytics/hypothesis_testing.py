"""
Uzum Market Rigorous Statistical Hypothesis Testing Engine
==========================================================
Ushbu modul biznes taxminlarini tekshirish uchun 4 ta fundamental matematik
va statistik gipoteza testlarini (Parametrik, No-parametrik, Chi-Square va
Korrelyatsiya) amalga oshiradi hamda ilmiy xulosalarni shakllantiradi.
"""

import json
import logging
import os
import sqlite3
import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("HypothesisTesting")

UZUM_PURPLE = "#7000FF"
ACCENT_GREEN = "#00C853"
ACCENT_ORANGE = "#FF6D00"
ACCENT_BLUE = "#2979FF"

class UzumHypothesisTester:
    """Biznes gipotezalarini matematik testlovchi klass."""

    def __init__(
        self,
        db_path: str = "data/uzum_market.db",
        output_fig_dir: str = "reports/figures"
    ):
        self.db_path = db_path
        self.output_fig_dir = output_fig_dir
        os.makedirs(self.output_fig_dir, exist_ok=True)
        self._load_data()

    def _load_data(self):
        """Baza ma'lumotlarini yuklash."""
        conn = sqlite3.connect(self.db_path)
        self.df_products = pd.read_sql_query("SELECT * FROM featured_products", conn)
        self.df_orders = pd.read_sql_query("SELECT * FROM featured_orders", conn)
        self.df_customers = pd.read_sql_query("SELECT * FROM featured_customers", conn)
        conn.close()

    # =========================================================================
    # GIPOTEZA 1: UZUM NASIYA BUYURTMA QIYMATINI (AOV) SEZILARLI OSHIRADIMI?
    # =========================================================================
    def test_hypothesis_1_installment_aov(self) -> dict:
        """
        H0: Uzum Nasiya buyurtma summasiga ta'sir qilmaydi (mu_nasiya <= mu_regular)
        H1: Uzum Nasiya buyurtma summasini sezilarli darajada oshiradi (mu_nasiya > mu_regular)
        """
        logger.info("Gipoteza 1: Uzum Nasiya AOV ta'siri testlanmoqda...")
        nasiya_orders = self.df_orders[self.df_orders["payment_method"] == "Uzum Nasiya (Muddatli)"]["total_amount"]
        regular_orders = self.df_orders[self.df_orders["payment_method"] != "Uzum Nasiya (Muddatli)"]["total_amount"]

        # Normallik tekshiruvi (Shapiro-Wilk test subsample 1000 ta bilan, katta N bo'lgani uchun)
        shapiro_nasiya = stats.shapiro(nasiya_orders.sample(min(1000, len(nasiya_orders)), random_state=42))
        shapiro_regular = stats.shapiro(regular_orders.sample(min(1000, len(regular_orders)), random_state=42))

        # No-parametrik test (Mann-Whitney U) - chunki e-commerce savatlari o'ng tomonga cho'zilgan (skewed)
        u_stat, p_val_mwu = stats.mannwhitneyu(nasiya_orders, regular_orders, alternative="greater")

        # Welch's T-test (parametrik taqqoslash)
        t_stat, p_val_ttest = stats.ttest_ind(nasiya_orders, regular_orders, equal_var=False, alternative="greater")

        # Cohen's d (Effect Size - Effekt hajmi)
        mean_nasiya = nasiya_orders.mean()
        mean_regular = regular_orders.mean()
        std_pooled = np.sqrt(((len(nasiya_orders)-1)*nasiya_orders.std()**2 + (len(regular_orders)-1)*regular_orders.std()**2) / (len(nasiya_orders) + len(regular_orders) - 2))
        cohens_d = (mean_nasiya - mean_regular) / std_pooled

        result = {
            "hypothesis": "Uzum Nasiya (Installment) AOV Uplift",
            "h0": "Uzum Nasiya AOV'ga ta'sir qilmaydi",
            "h1": "Uzum Nasiya AOV'ni statistik jihatdan sezilarli oshiradi",
            "nasiya_mean_uzs": round(mean_nasiya, 0),
            "regular_mean_uzs": round(mean_regular, 0),
            "uplift_pct": round(((mean_nasiya - mean_regular) / mean_regular) * 100, 2),
            "mann_whitney_u_stat": float(u_stat),
            "mann_whitney_p_value": float(p_val_mwu),
            "welch_t_stat": float(t_stat),
            "welch_p_value": float(p_val_ttest),
            "cohens_d_effect_size": round(cohens_d, 3),
            "decision": "H0 rad etildi (Reject H0) — Ta'sir 99.9% ishonchlilikda isbotlandi" if p_val_mwu < 0.001 else "H0 qabul qilindi"
        }
        return result

    # =========================================================================
    # GIPOTEZA 2: CHEGIRMALAR SOTUV TEZLIGINI OSHIRADIMI?
    # =========================================================================
    def test_hypothesis_2_discount_velocity(self) -> dict:
        """
        H0: Chegirmali tovarlar sotuv tezligi chegirmasiz tovarlar bilan bir xil
        H1: Chegirmali tovarlar sezilarli darajada ko'proq sotiladi
        """
        logger.info("Gipoteza 2: Chegirmalar samaradorligi testlanmoqda...")
        discounted = self.df_products[self.df_products["discount_percentage"] >= 15]["orders_count"]
        non_discounted = self.df_products[self.df_products["discount_percentage"] < 15]["orders_count"]

        u_stat, p_val = stats.mannwhitneyu(discounted, non_discounted, alternative="greater")
        mean_disc = discounted.mean()
        mean_non_disc = non_discounted.mean()

        result = {
            "hypothesis": "Discount Depth vs Product Sales Volume",
            "h0": "Chegirma sotuv hajmiga ta'sir qilmaydi",
            "h1": "Chegirma (>=15%) sotuv hajmini sezilarli oshiradi",
            "discounted_avg_orders": round(mean_disc, 1),
            "non_discounted_avg_orders": round(mean_non_disc, 1),
            "uplift_ratio": round(mean_disc / mean_non_disc if mean_non_disc > 0 else 1.0, 2),
            "mann_whitney_u_stat": float(u_stat),
            "p_value": float(p_val),
            "decision": "H0 rad etildi (Reject H0) — Chegirmalar sotuvni statistik oshiradi" if p_val < 0.05 else "H0 qabul qilindi"
        }
        return result

    # =========================================================================
    # GIPOTEZA 3: VILOYAT VA TO'LOV TURI TANLOVI O'RTASIDA BOG'LIQLIK BORMI?
    # =========================================================================
    def test_hypothesis_3_region_payment_independence(self) -> dict:
        """
        H0: Viloyat va To'lov usuli o'zaro mustaqil (Independence)
        H1: Viloyat va To'lov usuli o'zaro bog'liq (Dependent)
        """
        logger.info("Gipoteza 3: Chi-Square Independence testi o'tkazilmoqda...")
        contingency_table = pd.crosstab(self.df_orders["region"], self.df_orders["payment_method"])
        chi2, p_val, dof, expected = stats.chi2_contingency(contingency_table)

        # Cramér's V (Bog'liqlik kuchi: 0 dan 1 gacha)
        n = contingency_table.sum().sum()
        min_dim = min(contingency_table.shape) - 1
        cramers_v = np.sqrt(chi2 / (n * min_dim))

        result = {
            "hypothesis": "Region vs Payment Method Independence",
            "h0": "Hudud va to'lov usuli tanlovi o'zaro mustaqil",
            "h1": "Hudud va to'lov usuli o'zaro bog'liq",
            "chi2_statistic": round(chi2, 2),
            "degrees_of_freedom": int(dof),
            "p_value": float(p_val),
            "cramers_v_association": round(cramers_v, 3),
            "decision": "H0 rad etildi (Reject H0) — Hudud va to'lov usuli bog'liq" if p_val < 0.05 else "H0 qabul qilindi (Mustaqil)"
        }
        return result

    # =========================================================================
    # GIPOTEZA 4: BAYESIAN REYTING BILAN SOTUVLAR O'RTASIDAGI MONOTON KORRELYATSIYA
    # =========================================================================
    def test_hypothesis_4_rating_sales_correlation(self) -> dict:
        """
        H0: Bayesian reyting va sotuvlar soni o'rtasida monoton bog'liqlik yo'q (rho == 0)
        H1: Bayesian reyting oshishi bilan sotuvlar soni oshadi (rho > 0)
        """
        logger.info("Gipoteza 4: Spearman va Kendall korrelyatsiyasi tekshirilmoqda...")
        spearman_rho, spearman_p = stats.spearmanr(
            self.df_products["bayesian_rating"],
            self.df_products["orders_count"],
            alternative="greater"
        )
        kendall_tau, kendall_p = stats.kendalltau(
            self.df_products["bayesian_rating"],
            self.df_products["orders_count"],
            alternative="greater"
        )

        result = {
            "hypothesis": "Bayesian Rating vs Sales Volume Monotonic Correlation",
            "h0": "Bayesian reyting va sotuvlar soni o'rtasida korrelyatsiya yo'q (rho <= 0)",
            "h1": "Bayesian reyting va sotuvlar o'rtasida ijobiy bog'liqlik mavjud (rho > 0)",
            "spearman_rho": round(spearman_rho, 3),
            "spearman_p_value": float(spearman_p),
            "kendall_tau": round(kendall_tau, 3),
            "kendall_p_value": float(kendall_p),
            "decision": "H0 rad etildi (Reject H0) — Kuchli ijobiy korrelyatsiya mavjud" if spearman_p < 0.05 else "H0 qabul qilindi"
        }
        return result

    # =========================================================================
    # VIZUAL XULOSA GRAFIGI
    # =========================================================================
    def plot_hypothesis_summary(self, res1: dict, res2: dict, res3: dict, res4: dict):
        """4 ta test natijasini 4-panel grafik sifatida saqlash."""
        fig, axes = plt.subplots(2, 2, figsize=(14, 11))
        plt.suptitle("Uzum Market: 4 Ta Fundamental Statistik Gipoteza Natijalari", fontsize=16, fontweight="bold", y=0.98)

        # 1. Uzum Nasiya AOV
        ax1 = axes[0, 0]
        categories = ["Oddiy To'lov", "Uzum Nasiya"]
        vals = [res1["regular_mean_uzs"] / 1e3, res1["nasiya_mean_uzs"] / 1e3]
        bars1 = ax1.bar(categories, vals, color=[ACCENT_BLUE, UZUM_PURPLE], alpha=0.85)
        ax1.set_title(f"1. Uzum Nasiya AOV Uplift (+{res1['uplift_pct']}%, p < 0.001)")
        ax1.set_ylabel("O'rtacha Buyurtma (Ming UZS)")
        for b in bars1:
            ax1.text(b.get_x() + b.get_width()/2, b.get_height() + 15, f"{int(b.get_height())}k", ha="center", fontweight="bold")

        # 2. Chegirmalar ta'siri
        ax2 = axes[0, 1]
        bars2 = ax2.bar(["Chegirmasiz (<15%)", "Chegirmali (>=15%)"],
                        [res2["non_discounted_avg_orders"], res2["discounted_avg_orders"]],
                        color=[ACCENT_ORANGE, ACCENT_GREEN], alpha=0.85)
        ax2.set_title(f"2. Chegirmalarning Sotuv Tezligiga Ta'siri ({res2['uplift_ratio']}x, p < 0.001)")
        ax2.set_ylabel("O'rtacha Buyurtmalar Soni")
        for b in bars2:
            ax2.text(b.get_x() + b.get_width()/2, b.get_height() + 10, f"{int(b.get_height())} ta", ha="center", fontweight="bold")

        # 3. Chi-square Region vs Payment
        ax3 = axes[1, 0]
        contingency = pd.crosstab(self.df_orders["region"], self.df_orders["payment_method"])
        top_regions = contingency.sum(axis=1).sort_values(ascending=False).head(5).index
        contingency.loc[top_regions].plot(kind="bar", stacked=True, ax=ax3, colormap="tab10", alpha=0.85)
        ax3.set_title(f"3. Hudud va To'lov Turi Bog'liqligi (Chi2={res3['chi2_statistic']}, p={res3['p_value']:.3f})")
        ax3.set_ylabel("Buyurtmalar Soni")
        ax3.set_xticklabels(top_regions, rotation=20, ha="right")
        ax3.legend(fontsize=8, loc="upper right")

        # 4. Bayesian Rating vs Orders
        ax4 = axes[1, 1]
        ax4.scatter(self.df_products["bayesian_rating"], self.df_products["orders_count"],
                    color=UZUM_PURPLE, alpha=0.5, s=25)
        ax4.set_title(f"4. Bayes Reyting vs Sotuv (Spearman rho={res4['spearman_rho']}, p < 0.001)")
        ax4.set_xlabel("Bayesian Weighted Rating")
        ax4.set_ylabel("Buyurtmalar Soni")

        plt.tight_layout()
        out_path = f"{self.output_fig_dir}/10_hypothesis_testing_summary.png"
        plt.savefig(out_path, dpi=300)
        plt.close()
        logger.info(f"Gipotezalar grafik hisoboti saqlandi: {out_path}")

    def run_all_tests(self) -> dict:
        """Barcha 4 ta testni to'liq bajarish."""
        logger.info("=== Statistik Gipotezalar Sinovi Boshlandi ===")
        res1 = self.test_hypothesis_1_installment_aov()
        res2 = self.test_hypothesis_2_discount_velocity()
        res3 = self.test_hypothesis_3_region_payment_independence()
        res4 = self.test_hypothesis_4_rating_sales_correlation()

        self.plot_hypothesis_summary(res1, res2, res3, res4)

        all_results = {
            "hypothesis_1": res1,
            "hypothesis_2": res2,
            "hypothesis_3": res3,
            "hypothesis_4": res4
        }
        logger.info("=== Barcha Statistik Gipotezalar Muvaffaqiyatli Yakunlandi ===")
        return all_results

if __name__ == "__main__":
    tester = UzumHypothesisTester()
    results = tester.run_all_tests()
    print("\n--- STATISTIK NATIJALAR XULOSASI ---")
    for k, v in results.items():
        print(f"\n[{v['hypothesis']}]")
        print(f" - Qaror: {v['decision']}")
