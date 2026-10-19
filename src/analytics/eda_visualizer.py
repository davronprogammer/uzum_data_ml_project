"""
Uzum Market Professional EDA Visualization Suite
================================================
Ushbu modul 6 ta asosiy biznes savoliga javob beruvchi 24 ta yuqori
aniqlikdagi (300 DPI) vizual tasvirlarni generatsiya qiladi va
reports/figures/ katalogiga saqlaydi.
"""

import os
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Professional grafik uslubini o'rnatish
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["font.size"] = 11
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["axes.labelsize"] = 12
plt.rcParams["figure.titlesize"] = 16

UZUM_PURPLE = "#7000FF"
UZUM_YELLOW = "#FFFF00"
ACCENT_GREEN = "#00C853"
ACCENT_ORANGE = "#FF6D00"
ACCENT_BLUE = "#2979FF"
DARK_SLATE = "#1F1F26"

class UzumEDAVisualizer:
    """Professional vizualizatsiyalar generatori."""

    def __init__(
        self,
        db_path: str = "data/uzum_market.db",
        output_dir: str = "reports/figures"
    ):
        self.db_path = db_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self._load_data()

    def _load_data(self):
        """Ma'lumotlar bazasidan tahliliy jadvallarni o'qish."""
        conn = sqlite3.connect(self.db_path)
        self.df_products = pd.read_sql_query("SELECT * FROM featured_products", conn)
        self.df_orders = pd.read_sql_query("SELECT * FROM featured_orders", conn)
        self.df_customers = pd.read_sql_query("SELECT * FROM featured_customers", conn)
        self.df_order_items = pd.read_sql_query("SELECT * FROM order_items", conn)
        conn.close()

    # ==========================================
    # MAVZU 1: GEOGRAFIK TALAB (4 ta grafik)
    # ==========================================
    def generate_theme_1_geography(self):
        print("Mavzu 1: Geografik talab grafiklari generatsiya qilinmoqda...")

        # 1.1: Viloyatlar bo'yicha GMV va buyurtmalar
        region_stats = self.df_orders.groupby("region").agg(
            total_gmv=("total_amount", lambda x: x.sum() / 1e9),
            orders_count=("order_id", "count")
        ).sort_values("total_gmv", ascending=True)

        fig, ax1 = plt.subplots(figsize=(12, 7))
        y_pos = np.arange(len(region_stats))
        ax1.barh(y_pos, region_stats["total_gmv"], color=UZUM_PURPLE, alpha=0.85, label="GMV (Milliard so'm)")
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(region_stats.index, fontweight="bold")
        ax1.set_xlabel("Umumiy aylanma GMV (Milliard UZS)", color=UZUM_PURPLE)

        for i, v in enumerate(region_stats["total_gmv"]):
            ax1.text(v + 0.1, i, f"{v:.1f} mlrd", va="center", fontsize=10, fontweight="bold")

        plt.title("1.1. O'zbekiston Viloyatlari Bo'yicha Savdo Aylanmasi (GMV)", pad=15)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/01_01_regional_gmv_volume.png", dpi=300)
        plt.close()

        # 1.2: Toshkent vs Viloyatlar nisbati (Donut chart)
        is_tashkent = self.df_orders["region"].apply(lambda x: "Toshkent shahri" if "Toshkent shahri" in x else "Viloyatlar")
        tash_counts = is_tashkent.value_counts()
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(tash_counts, labels=tash_counts.index, autopct="%1.1f%%", startangle=90,
               colors=[UZUM_PURPLE, ACCENT_BLUE], wedgeprops=dict(width=0.45, edgecolor="w", linewidth=3),
               textprops=dict(fontsize=13, fontweight="bold"))
        plt.title("1.2. Toshkent Shahri va Viloyatlar Savdo Ulushi Nisbati", pad=15)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/01_02_tashkent_vs_regions_share.png", dpi=300)
        plt.close()

        # 1.3: Hududlar bo'yicha O'rtacha Buyurtma Qiymati (AOV)
        aov_by_region = self.df_orders.groupby("region")["total_amount"].mean().sort_values(ascending=False) / 1e3
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(aov_by_region.index, aov_by_region.values, color=ACCENT_ORANGE, alpha=0.85)
        ax.set_ylabel("O'rtacha chek AOV (Ming UZS)")
        plt.xticks(rotation=45, ha="right", fontweight="bold")
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2.0, yval + 10, f"{int(yval)}k", ha="center", va="bottom", fontsize=9, fontweight="bold")
        plt.title("1.3. O'zbekiston Hududlari Bo'yicha O'rtacha Buyurtma Qiymati (AOV)", pad=15)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/01_03_regional_aov_comparison.png", dpi=300)
        plt.close()

        # 1.4: Yetkazib berish turi ulushi (PVZ vs Kuryer)
        deliv_cross = pd.crosstab(self.df_orders["region"], self.df_orders["delivery_type"], normalize="index") * 100
        deliv_cross = deliv_cross.sort_values(deliv_cross.columns[0], ascending=True)
        fig, ax = plt.subplots(figsize=(12, 7))
        deliv_cross.plot(kind="barh", stacked=True, color=[UZUM_PURPLE, ACCENT_GREEN], ax=ax, alpha=0.9)
        ax.set_xlabel("Ulush (%)")
        plt.title("1.4. Hududlar Bo'yicha Yetkazib Berish Turi (PVZ vs Kuryer)", pad=15)
        plt.legend(title="Yetkazish usuli", loc="lower right")
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/01_04_delivery_type_by_region.png", dpi=300)
        plt.close()

    # ==========================================
    # MAVZU 2: FINTECH VA TO'LOV TURLARI (4 ta grafik)
    # ==========================================
    def generate_theme_2_fintech(self):
        print("Mavzu 2: Fintex va to'lov turlari grafiklari generatsiya qilinmoqda...")

        # 2.1: To'lov usullari bo'yicha tranzaksiyalar va GMV ulushi
        pay_summary = self.df_orders.groupby("payment_method").agg(
            transactions=("order_id", "count"),
            gmv=("total_amount", "sum")
        )
        pay_summary["tx_pct"] = (pay_summary["transactions"] / pay_summary["transactions"].sum()) * 100
        pay_summary["gmv_pct"] = (pay_summary["gmv"] / pay_summary["gmv"].sum()) * 100
        pay_summary = pay_summary.sort_values("gmv_pct", ascending=False)

        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.arange(len(pay_summary))
        width = 0.35
        ax.bar(x - width/2, pay_summary["tx_pct"], width, label="Tranzaksiyalar soni ulushi (%)", color=ACCENT_BLUE)
        ax.bar(x + width/2, pay_summary["gmv_pct"], width, label="Umumiy aylanma (GMV) ulushi (%)", color=UZUM_PURPLE)
        ax.set_xticks(x)
        ax.set_xticklabels(pay_summary.index, rotation=20, ha="right", fontweight="bold")
        ax.set_ylabel("Ulush (%)")
        plt.title("2.1. To'lov Usullari: Tranzaksiya Soni vs Moliya Aylanmasi (GMV)", pad=15)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/02_01_payment_method_market_share.png", dpi=300)
        plt.close()

        # 2.2: Mahsulot narx toifalarida to'lov usullari (Stacked bar)
        items_with_payment = self.df_order_items.merge(self.df_orders[["order_id", "payment_method"]], on="order_id")
        items_with_payment = items_with_payment.merge(self.df_products[["product_id", "price_segment"]], on="product_id")
        seg_pay = pd.crosstab(items_with_payment["price_segment"], items_with_payment["payment_method"], normalize="index") * 100
        fig, ax = plt.subplots(figsize=(10, 6))
        seg_pay.plot(kind="bar", stacked=True, ax=ax, colormap="viridis", alpha=0.9)
        plt.xticks(rotation=0, fontweight="bold")
        ax.set_ylabel("Ulush (%)")
        plt.title("2.2. Narx Segmentlari Bo'yicha To'lov Usullari Taqsimoti", pad=15)
        plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/02_02_payment_by_price_segment.png", dpi=300)
        plt.close()

        # 2.3: Hududlar va to'lov usullari heatmapi
        region_pay = pd.crosstab(self.df_orders["region"], self.df_orders["payment_method"], normalize="index") * 100
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(region_pay, annot=True, fmt=".1f", cmap="Purples", ax=ax, cbar_kws={'label': 'Ulush (%)'})
        plt.title("2.3. Viloyatlar Bo'yicha To'lov Usullari Penetratsiyasi (Heatmap)", pad=15)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/02_03_payment_by_region_heatmap.png", dpi=300)
        plt.close()

        # 2.4: Oylar bo'yicha to'lov turlari dinamikasi
        orders_month = self.df_orders.copy()
        orders_month["order_month_dt"] = pd.to_datetime(orders_month["order_date"]).dt.to_period("M").astype(str)
        monthly_pay = pd.crosstab(orders_month["order_month_dt"], orders_month["payment_method"], normalize="index") * 100
        fig, ax = plt.subplots(figsize=(12, 6))
        for col in monthly_pay.columns:
            ax.plot(monthly_pay.index, monthly_pay[col], marker="o", linewidth=2.5, label=col)
        plt.xticks(rotation=45, ha="right", fontweight="bold")
        ax.set_ylabel("Oylik Ulush (%)")
        plt.title("2.4. To'lov Usullarining Oylik O'sish Va Barqarorlik Trendi", pad=15)
        plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/02_04_monthly_payment_trend.png", dpi=300)
        plt.close()

    # ==========================================
    # MAVZU 3: UZUM NASIYA SAMARADORLIGI (4 ta grafik)
    # ==========================================
    def generate_theme_3_installment(self):
        print("Mavzu 3: Uzum Nasiya samaradorligi grafiklari generatsiya qilinmoqda...")

        # 3.1: Nasiyali vs Nasiyasiz buyurtmalar AOV taqqoslovi
        is_nasiya = self.df_orders["payment_method"] == "Uzum Nasiya (Muddatli)"
        aov_nasiya = self.df_orders[is_nasiya]["total_amount"]
        aov_other = self.df_orders[~is_nasiya]["total_amount"]

        fig, ax = plt.subplots(figsize=(8, 6))
        box_data = [aov_other / 1e3, aov_nasiya / 1e3]
        bp = ax.boxplot(box_data, patch_artist=True, tick_labels=["Oddiy To'lovlar", "Uzum Nasiya"], showfliers=False)
        colors = [ACCENT_BLUE, UZUM_PURPLE]
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.8)
        ax.set_ylabel("Buyurtma Qiymati (Ming UZS)")
        
        mean_other = (aov_other.median() / 1e3)
        mean_nasiya = (aov_nasiya.median() / 1e3)
        ax.text(1, mean_other, f"Mediana: {mean_other:.0f}k", horizontalalignment='center', color='white', fontweight='bold')
        ax.text(2, mean_nasiya, f"Mediana: {mean_nasiya:.0f}k", horizontalalignment='center', color='white', fontweight='bold')

        plt.title("3.1. Uzum Nasiya va Oddiy To'lovlar O'rtacha Cheki (AOV) Taqqoslovi", pad=15)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/03_01_installment_vs_regular_aov.png", dpi=300)
        plt.close()

        # 3.2: Nasiya bor va yo'q tovarlar savdo tezligi (Orders count)
        fig, ax = plt.subplots(figsize=(10, 6))
        has_inst = self.df_products.groupby("has_installment")["orders_count"].mean()
        bars = ax.bar(["Nasiyasiz Tovarlar", "Uzum Nasiya Bor Tovarlar"], has_inst.values, color=[DARK_SLATE, UZUM_PURPLE], alpha=0.85)
        ax.set_ylabel("O'rtacha Buyurtmalar Soni")
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2.0, yval + 10, f"{int(yval)} dona", ha="center", va="bottom", fontsize=11, fontweight="bold")
        plt.title("3.2. Muddatli To'lov Imkoniyati va Tovarning O'rtacha Sotuv Hajmi", pad=15)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/03_02_installment_sales_velocity.png", dpi=300)
        plt.close()

        # 3.3: Oylik to'lov va umumiy narx korrelyatsiyasi (Scatter plot)
        inst_products = self.df_products[self.df_products["has_installment"] == 1]
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(inst_products["price_current"] / 1e6, inst_products["monthly_installment"] / 1e3,
                   alpha=0.6, color=UZUM_PURPLE, edgecolors="none", s=40)
        ax.set_xlabel("Mahsulot Narxi (Million UZS)")
        ax.set_ylabel("Oylik Muddatli To'lov (Ming UZS/oy)")
        plt.title("3.3. Tovar Narxi va Uzum Nasiya Oylik To'lovi Nisbati", pad=15)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/03_03_installment_price_scatter.png", dpi=300)
        plt.close()

        # 3.4: Narx segmentlari bo'yicha Nasiya penetratsiyasi
        inst_by_seg = self.df_products.groupby("price_segment")["has_installment"].mean() * 100
        fig, ax = plt.subplots(figsize=(8, 6))
        bars = ax.bar(inst_by_seg.index, inst_by_seg.values, color=ACCENT_GREEN, alpha=0.85)
        ax.set_ylabel("Nasiya Qamrovi (%)")
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2.0, yval + 1, f"{yval:.1f}%", ha="center", va="bottom", fontsize=11, fontweight="bold")
        plt.title("3.4. Narx Segmentlari Bo'yicha Uzum Nasiya Qamrovi Ulushi", pad=15)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/03_04_installment_coverage_by_segment.png", dpi=300)
        plt.close()

    # ==========================================
    # MAVZU 4: REYTINGLAR VA BAYESIAN SMOOTHING (4 ta grafik)
    # ==========================================
    def generate_theme_4_ratings(self):
        print("Mavzu 4: Reytinglar va Bayesian smoothing grafiklari generatsiya qilinmoqda...")

        # 4.1: Xom reyting taqsimoti
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.histplot(self.df_products["rating"], bins=25, kde=True, color=ACCENT_ORANGE, ax=ax)
        ax.set_xlabel("Xaridorlar Bergan Xom Reyting (Raw Rating)")
        ax.set_ylabel("Mahsulotlar Soni")
        plt.title("4.1. Xom Reytinglar Taqsimoti (5.0 ga qarab og'ish anomaliyasi)", pad=15)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/04_01_raw_rating_distribution.png", dpi=300)
        plt.close()

        # 4.2: Bayesian Weighted Rating taqsimoti
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.histplot(self.df_products["bayesian_rating"], bins=25, kde=True, color=UZUM_PURPLE, ax=ax)
        ax.set_xlabel("Bayesian Weighted Rating (Silliqlangan Reyting)")
        ax.set_ylabel("Mahsulotlar Soni")
        plt.title("4.2. Bayesian Silliqlashdan Keyingi Realistik Reyting Taqsimoti", pad=15)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/04_02_bayesian_rating_distribution.png", dpi=300)
        plt.close()

        # 4.3: Sharhlar soni va Reyting (Raw vs Bayes)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        ax1.scatter(self.df_products["reviews_count"], self.df_products["rating"], color=ACCENT_ORANGE, alpha=0.5, s=25)
        ax1.set_title("Xom Reyting vs Sharhlar Soni")
        ax1.set_xlabel("Sharhlar Soni")
        ax1.set_ylabel("Raw Rating")
        ax1.set_xscale("log")

        ax2.scatter(self.df_products["reviews_count"], self.df_products["bayesian_rating"], color=UZUM_PURPLE, alpha=0.5, s=25)
        ax2.set_title("Bayesian Rating vs Sharhlar Soni")
        ax2.set_xlabel("Sharhlar Soni (Log shkala)")
        ax2.set_ylabel("Bayesian Rating")
        ax2.set_xscale("log")

        plt.suptitle("4.3. Bayes Modeli Qanday Qilib Kam Sharhli Soxta 5.0 larni Zararsizlantirdi", y=1.02, fontsize=15, fontweight="bold")
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/04_03_bayes_vs_raw_scatter.png", dpi=300)
        plt.close()

        # 4.4: Reyting oraliqlari bo'yicha o'rtacha buyurtmalar soni
        self.df_products["rating_bracket"] = pd.cut(
            self.df_products["bayesian_rating"],
            bins=[0, 4.0, 4.5, 4.8, 5.0],
            labels=["< 4.0", "4.0 - 4.5", "4.5 - 4.8", "4.8 - 5.0"]
        )
        orders_by_bracket = self.df_products.groupby("rating_bracket", observed=False)["orders_count"].mean()
        fig, ax = plt.subplots(figsize=(8, 6))
        bars = ax.bar(orders_by_bracket.index.astype(str), orders_by_bracket.values, color=ACCENT_BLUE, alpha=0.85)
        ax.set_ylabel("O'rtacha Buyurtmalar Soni")
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2.0, yval + 10, f"{int(yval)} dona", ha="center", va="bottom", fontsize=11, fontweight="bold")
        plt.title("4.4. Bayesian Reyting Guruhlari Bo'yicha O'rtacha Sotuv Hajmi", pad=15)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/04_04_orders_by_rating_bracket.png", dpi=300)
        plt.close()

    # ==========================================
    # MAVZU 5: CHEGIRMALAR VA NARXLASH (4 ta grafik)
    # ==========================================
    def generate_theme_5_discounts(self):
        print("Mavzu 5: Chegirmalar va narxlash grafiklari generatsiya qilinmoqda...")

        # 5.1: Chegirma darajalari bo'yicha tovarlar soni va umumiy sotuv
        disc_summary = self.df_products.groupby("discount_tier").agg(
            products_count=("product_id", "count"),
            avg_orders=("orders_count", "mean")
        ).reindex(["No Discount", "Low (1-15%)", "Moderate (15-30%)", "Deep (>30%)"])

        fig, ax1 = plt.subplots(figsize=(10, 6))
        x = np.arange(len(disc_summary))
        width = 0.35
        ax1.bar(x - width/2, disc_summary["products_count"], width, label="Mahsulotlar Soni", color=DARK_SLATE, alpha=0.8)
        ax2 = ax1.twinx()
        ax2.bar(x + width/2, disc_summary["avg_orders"], width, label="O'rtacha Buyurtmalar Soni", color=ACCENT_ORANGE, alpha=0.85)
        ax1.set_xticks(x)
        ax1.set_xticklabels(disc_summary.index, fontweight="bold")
        ax1.set_ylabel("Mahsulotlar Soni")
        ax2.set_ylabel("O'rtacha Buyurtmalar Soni")
        plt.title("5.1. Chegirma Darajalari: Mahsulotlar Soni vs O'rtacha Sotuv Hajmi", pad=15)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/05_01_discount_tier_impact.png", dpi=300)
        plt.close()

        # 5.2: Chegirma foizi vs Sotuv hajmi (Scatter)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(self.df_products["discount_percentage"], self.df_products["orders_count"],
                   alpha=0.5, color=ACCENT_GREEN, edgecolors="none")
        ax.set_xlabel("Chegirma Foizi (%)")
        ax.set_ylabel("Buyurtmalar Soni (Orders)")
        plt.title("5.2. Chegirma Intensivligi va Mahsulot Sotuv Hajmi Bog'liqligi", pad=15)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/05_02_discount_vs_orders_scatter.png", dpi=300)
        plt.close()

        # 5.3: Narx segmentlari bo'yicha o'rtacha chegirma
        fig, ax = plt.subplots(figsize=(8, 6))
        disc_by_seg = self.df_products.groupby("price_segment")["discount_percentage"].mean()
        bars = ax.bar(disc_by_seg.index, disc_by_seg.values, color=UZUM_PURPLE, alpha=0.85)
        ax.set_ylabel("O'rtacha Chegirma (%)")
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.3, f"{yval:.1f}%", ha="center", va="bottom", fontsize=11, fontweight="bold")
        plt.title("5.3. Narx Segmentlari Bo'yicha O'rtacha Chegirma Foizi", pad=15)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/05_03_discount_by_price_segment.png", dpi=300)
        plt.close()

        # 5.4: Chegirma mavjudligi bo'yicha daromadlilik ulushi
        self.df_products["has_discount"] = (self.df_products["discount_percentage"] > 0).astype(int)
        disc_orders = self.df_products.groupby("has_discount")["orders_count"].sum()
        fig, ax = plt.subplots(figsize=(7, 7))
        ax.pie(disc_orders, labels=["Chegirmasiz", "Chegirmali"], autopct="%1.1f%%",
               colors=[ACCENT_BLUE, ACCENT_ORANGE], startangle=90,
               wedgeprops=dict(width=0.45, edgecolor="w", linewidth=3), textprops=dict(fontsize=13, fontweight="bold"))
        plt.title("5.4. Sotilgan Jami Tovarlar Ichida Chegirmali Mahsulotlar Ulushi", pad=15)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/05_04_discount_sales_volume_share.png", dpi=300)
        plt.close()

    # ==========================================
    # MAVZU 6: MAVSUMIY TO'LQINLAR VA VAQT SIKLLARI (4 ta grafik)
    # ==========================================
    def generate_theme_6_seasonality(self):
        print("Mavzu 6: Mavsumiylik va vaqt sikllari grafiklari generatsiya qilinmoqda...")

        # 6.1: Kunlik aylanma dinamikasi (Time series trend)
        daily_sales = self.df_orders.groupby("order_date").agg(
            daily_gmv=("total_amount", lambda x: x.sum() / 1e6)
        ).reset_index()
        daily_sales["order_date_dt"] = pd.to_datetime(daily_sales["order_date"])
        daily_sales = daily_sales.sort_values("order_date_dt")

        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(daily_sales["order_date_dt"], daily_sales["daily_gmv"], color=UZUM_PURPLE, linewidth=1.8, label="Kunlik GMV (Mln UZS)")
        
        # 7 kunlik siljishli o'rtacha (Rolling 7d average)
        daily_sales["rolling_7d"] = daily_sales["daily_gmv"].rolling(7, min_periods=1).mean()
        ax.plot(daily_sales["order_date_dt"], daily_sales["rolling_7d"], color=ACCENT_ORANGE, linewidth=2.5, linestyle="--", label="7 kunlik trend")

        ax.set_ylabel("Kunlik GMV (Million UZS)")
        plt.title("6.1. 1 Yillik Savdo Dinamikasi va Mavsumiy Piklar (11.11, Yangi Yil, Navro'z)", pad=15)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/06_01_daily_sales_timeline.png", dpi=300)
        plt.close()

        # 6.2: Savdo kampaniyalari bo'yicha o'rtacha kunlik ko'rsatkich
        camp_stats = self.df_orders.groupby("campaign_period")["total_amount"].mean() / 1e3
        camp_stats = camp_stats.sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(camp_stats.index, camp_stats.values, color=ACCENT_GREEN, alpha=0.85)
        ax.set_ylabel("O'rtacha Chek AOV (Ming UZS)")
        plt.xticks(rotation=25, ha="right", fontweight="bold")
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2.0, yval + 10, f"{int(yval)}k", ha="center", va="bottom", fontsize=10, fontweight="bold")
        plt.title("6.2. Maxsus Bayram va Aksiyalar Davrida O'rtacha Savat Kattaligi (AOV)", pad=15)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/06_02_campaign_aov_comparison.png", dpi=300)
        plt.close()

        # 6.3: Hafta kunlari va soatlar bo'yicha xarid faolligi heatmapi
        dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        heat_data = pd.crosstab(self.df_orders["day_of_week"], self.df_orders["order_hour"]).reindex(dow_order)
        fig, ax = plt.subplots(figsize=(14, 6))
        sns.heatmap(heat_data, cmap="YlGnBu", ax=ax, cbar_kws={'label': 'Buyurtmalar soni'})
        ax.set_ylabel("Hafta Kuni")
        ax.set_xlabel("Kun Soati (00:00 - 23:00)")
        plt.title("6.3. Hafta Kunlari va Kun Soatlari Bo'yicha Xaridorlar Faolligi (Heatmap)", pad=15)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/06_03_day_hour_activity_heatmap.png", dpi=300)
        plt.close()

        # 6.4: Dam olish kunlari (Weekend) vs Ish kunlari savdosi
        weekend_summary = self.df_orders.groupby("is_weekend").agg(
            avg_orders_per_day=("order_id", "count"),
            avg_order_value=("total_amount", "mean")
        )
        fig, ax = plt.subplots(figsize=(8, 6))
        bars = ax.bar(["Ish Kunlari (Dush-Juma)", "Dam Olish Kunlari (Shan-Yak)"], weekend_summary["avg_order_value"] / 1e3,
                      color=[DARK_SLATE, UZUM_PURPLE], alpha=0.85)
        ax.set_ylabel("O'rtacha Buyurtma Qiymati (Ming UZS)")
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2.0, yval + 8, f"{int(yval)}k UZS", ha="center", va="bottom", fontsize=11, fontweight="bold")
        plt.title("6.4. Ish Kunlari va Dam Olish Kunlari Xaridlari Taqqoslovi", pad=15)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/06_04_weekend_vs_weekday_aov.png", dpi=300)
        plt.close()

    def run_all(self):
        """Barcha 24 ta grafikni ketma-ket yaratish."""
        print("=== 24 ta Professional EDA Vizualizatsiyasi Boshlandi ===")
        self.generate_theme_1_geography()
        self.generate_theme_2_fintech()
        self.generate_theme_3_installment()
        self.generate_theme_4_ratings()
        self.generate_theme_5_discounts()
        self.generate_theme_6_seasonality()
        print(f"=== Barcha 24 ta grafik muvaffaqiyatli saqlandi: {self.output_dir} ===")

if __name__ == "__main__":
    vis = UzumEDAVisualizer()
    vis.run_all()
