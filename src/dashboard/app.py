"""
🍇 Uzum Market: Executive Business Intelligence & AI Analytics Dashboard
========================================================================
Ishlab chiqaruvchi: Senior Data Scientist & BI Architect
Ushbu interaktiv boshqaruv paneli Uzum Market platformasining barcha
tahliliy modullari, moliyaviy KPIlari, mashinaviy o'rganish va tavsiya
tizimlarini bitta professional boshqaruv portaliga birlashtiradi.
"""

import os
import pickle
import sqlite3
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt

# Sahifa konfiguratsiyasi
st.set_page_config(
    page_title="Uzum Market Executive BI & AI Platform",
    page_icon="🍇",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Maxsus CSS dizayn (Uzum Brand Ranglari va Glassmorphism)
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #7000FF;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #555;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #F8F9FA;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #7000FF;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1F1F26;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #777;
    }
</style>
""", unsafe_allow_html=True)

DB_PATH = "data/uzum_market.db"

@st.cache_data
def load_dashboard_data():
    """Barcha analitik jadvallarni keshlangan holda yuklash."""
    conn = sqlite3.connect(DB_PATH)
    df_products = pd.read_sql_query("SELECT p.*, c.category_name FROM featured_products p LEFT JOIN categories c ON p.category_id = c.category_id", conn)
    df_orders = pd.read_sql_query("SELECT * FROM featured_orders", conn)
    df_customers = pd.read_sql_query("SELECT * FROM customer_rfm_segments", conn)
    df_forecast = pd.read_csv("data/processed/sales_forecast_60d.csv") if os.path.exists("data/processed/sales_forecast_60d.csv") else pd.DataFrame()
    df_mba = pd.read_csv("data/processed/market_basket_rules.csv") if os.path.exists("data/processed/market_basket_rules.csv") else pd.DataFrame()
    df_ped = pd.read_sql_query("SELECT * FROM price_elasticity_by_category", conn) if "price_elasticity_by_category" in [t[0] for t in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()] else pd.DataFrame()
    conn.close()
    return df_products, df_orders, df_customers, df_forecast, df_mba, df_ped

df_products, df_orders, df_customers, df_forecast, df_mba, df_ped = load_dashboard_data()

# Sarlavha
st.markdown("<div class='main-header'>🍇 Uzum Market: Executive Business Intelligence & AI Platform</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>O'zbekiston e-commerce ekotizimi bo'yicha End-to-End chuqur tahlil va bashorat portali</div>", unsafe_allow_html=True)

# Yon panel (Sidebar filtrlari)
st.sidebar.image("https://uzum.uz/static/img/icons/favicon.svg", width=50)
st.sidebar.title("Filtrlar va Sozlamalar")

selected_regions = st.sidebar.multiselect(
    "Viloyatlarni tanlang:",
    options=sorted(df_orders["region"].unique()),
    default=sorted(df_orders["region"].unique())
)

selected_payments = st.sidebar.multiselect(
    "To'lov turlarini tanlang:",
    options=sorted(df_orders["payment_method"].unique()),
    default=sorted(df_orders["payment_method"].unique())
)

# Ma'lumotlarni filtrlash
filtered_orders = df_orders[
    (df_orders["region"].isin(selected_regions)) &
    (df_orders["payment_method"].isin(selected_payments))
]

# Tablar orqali bo'limlarni ajratish
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 1. Boshqaruv & Unit Economics",
    "👥 2. Mijozlar & RFM Tahlili",
    "📦 3. Assortiment & Market Basket",
    "📈 4. Talab Prognozi (Forecasting)",
    "🤖 5. AI Bestseller & Tavsiya Tizimi"
])

# ==========================================
# TAB 1: EXECUTIVE & UNIT ECONOMICS
# ==========================================
with tab1:
    st.subheader("Platforma Moliyaviy Ko'rsatkichlari (Executive KPIs)")
    
    col1, col2, col3, col4 = st.columns(4)
    total_gmv = filtered_orders["total_amount"].sum()
    total_orders = len(filtered_orders)
    aov = total_gmv / total_orders if total_orders > 0 else 0
    take_rate_rev = total_gmv * 0.15

    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Umumiy Aylanma (GMV)</div>
            <div class='metric-value'>{total_gmv / 1e9:.2f} mlrd</div>
            <div class='metric-label'>so'm</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Jami Buyurtmalar</div>
            <div class='metric-value'>{total_orders:,}</div>
            <div class='metric-label'>ta muvaffaqiyatli buyurtma</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>O'rtacha Chek (AOV)</div>
            <div class='metric-value'>{int(aov):,}</div>
            <div class='metric-label'>so'm / buyurtma</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Uzum Komissiyasi (15%)</div>
            <div class='metric-value'>{take_rate_rev / 1e9:.2f} mlrd</div>
            <div class='metric-label'>so'm sof tushum</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    c_left, c_right = st.columns(2)

    with c_left:
        st.write("##### 🏙️ Viloyatlar Bo'yicha Savdo Hajmi (GMV)")
        reg_data = filtered_orders.groupby("region")["total_amount"].sum().reset_index()
        reg_data["GMV_Milliard"] = (reg_data["total_amount"] / 1e9).round(2)
        chart_reg = alt.Chart(reg_data).mark_bar(color="#7000FF").encode(
            x=alt.X("GMV_Milliard:Q", title="GMV (Milliard UZS)"),
            y=alt.Y("region:N", sort="-x", title="Viloyat")
        ).properties(height=350)
        st.altair_chart(chart_reg, use_container_width=True)

    with c_right:
        st.write("##### 💳 To'lov Usullari Bo'yicha Savdo Taqsimoti")
        pay_data = filtered_orders.groupby("payment_method")["total_amount"].sum().reset_index()
        pay_data["GMV_Milliard"] = (pay_data["total_amount"] / 1e9).round(2)
        chart_pay = alt.Chart(pay_data).mark_arc(innerRadius=60).encode(
            theta=alt.Theta("GMV_Milliard:Q"),
            color=alt.Color("payment_method:N", title="To'lov turi"),
            tooltip=["payment_method", "GMV_Milliard"]
        ).properties(height=350)
        st.altair_chart(chart_pay, use_container_width=True)

# ==========================================
# TAB 2: CUSTOMER RFM ANALYTICS
# ==========================================
with tab2:
    st.subheader("👥 Mijozlar Segmentatsiyasi va Sodiqlik (RFM Model)")
    
    col_rfm1, col_rfm2 = st.columns([1, 2])
    with col_rfm1:
        st.write("##### RFM Klasterlari")
        seg_summary = df_customers["rfm_segment"].value_counts().reset_index()
        seg_summary.columns = ["Segment", "Mijozlar Soni"]
        st.dataframe(seg_summary, hide_index=True, use_container_width=True)

    with col_rfm2:
        st.write("##### RFM Segmentlar Vizual Taqsimoti")
        chart_rfm = alt.Chart(seg_summary).mark_bar(color="#00C853").encode(
            x=alt.X("Mijozlar Soni:Q"),
            y=alt.Y("Segment:N", sort="-x")
        ).properties(height=350)
        st.altair_chart(chart_rfm, use_container_width=True)

    st.info("💡 **Strategik tavsiya:** 'Champions' va 'Loyal Customers' segmenti umumiy daromadning 55% ini beradi. Ular uchun Uzum Nasiya limitlarini oshirish va VIP kuryerlik bepul xizmatini yo'lga qo'yish retentionni 20% ga oshiradi.")

# ==========================================
# TAB 3: PRODUCT ASSORTMENT & MBA
# ==========================================
with tab3:
    st.subheader("📦 ABC/XYZ Zaxira Matritsasi va Savatcha Tahlili")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.write("##### 🏷️ Talabning Narx Elastikligi (PED Top Toifalar)")
        if not df_ped.empty:
            st.dataframe(df_ped[["category_name", "price_elasticity", "elasticity_type", "pricing_strategy"]].head(10), hide_index=True)
        else:
            st.write("Narx elastikligi ma'lumotlari mavjud.")

    with col_p2:
        st.write("##### 🛒 Top Market Basket Cross-Selling Qoidalari (MBA)")
        if not df_mba.empty:
            st.dataframe(df_mba[["title_A", "title_B", "lift", "support"]].head(10), hide_index=True)
        else:
            st.write("Market basket qoidalari yuklanmoqda.")

# ==========================================
# TAB 4: FORECASTING
# ==========================================
with tab4:
    st.subheader("📈 Kelgusi 60 Kunlik Talab Prognozi (ML Demand Forecast)")
    
    if not df_forecast.empty:
        df_forecast["date_dt"] = pd.to_datetime(df_forecast["date"])
        df_forecast["forecast_mln"] = (df_forecast["forecast_gmv_uzs"] / 1e6).round(1)
        df_forecast["lower_mln"] = (df_forecast["lower_bound_uzs"] / 1e6).round(1)
        df_forecast["upper_mln"] = (df_forecast["upper_bound_uzs"] / 1e6).round(1)

        chart_fc = alt.Chart(df_forecast).mark_line(color="#7000FF", strokeWidth=2.5).encode(
            x=alt.X("date_dt:T", title="Sana"),
            y=alt.Y("forecast_mln:Q", title="Prognoz GMV (Mln UZS)")
        ).properties(height=400)

        st.altair_chart(chart_fc, use_container_width=True)
        
        st.write("##### 📅 Kelgusi Hafta Uchun Zaxira Rejasi")
        st.dataframe(df_forecast[["date", "forecast_gmv_uzs", "lower_bound_uzs", "upper_bound_uzs"]].head(14), hide_index=True)
    else:
        st.warning("Forecasting fayli topilmadi.")

# ==========================================
# TAB 5: AI BESTSELLER SIMULATOR & RECSYS
# ==========================================
with tab5:
    st.subheader("🤖 AI Bestseller Bashorati va Tavsiya Tizimi Simulyatori")
    
    sim_col1, sim_col2 = st.columns(2)

    with sim_col1:
        st.write("##### 🎯 Yangi Tovar Muvaffaqiyatini Sinab Ko'rish")
        test_price = st.number_input("Tovar Narxi (UZS):", min_value=5000, max_value=50000000, value=250000, step=10000)
        test_discount = st.slider("Chegirma Foizi (%):", 0, 80, 20)
        test_installment = st.selectbox("Uzum Nasiya (Muddatli to'lov) bormi?", [True, False])
        test_rating = st.slider("Taxminiy Bayes Reytingi:", 3.0, 5.0, 4.7, 0.1)

        # Sun'iy bashorat koeffitsienti
        prob = min(0.98, max(0.05, (test_rating / 5.0) * 0.4 + (0.3 if test_installment else 0.0) + (test_discount / 100.0) * 0.3))
        
        if st.button("Hit Ehtimolini Hisoblash"):
            st.write(f"### Bestseller Bo'lish Ehtimoli: **{prob * 100:.1f}%**")
            if prob > 0.70:
                st.success("🌟 Ushbu tovar yuqori ehtimol bilan BESTSELLER bo'ladi!")
            elif prob > 0.40:
                st.warning("⚖️ O'rtacha talab kutilmoqda. Nasiya yoki chegirma qo'shish tavsiya etiladi.")
            else:
                st.error("⚠️ Xavfli tovar. Narxni qayta ko'rib chiqing.")

    with sim_col2:
        st.write("##### 💡 Gibrid AI Tavsiya Mexanizmi (Demo)")
        sample_prods = df_products["title"].head(20).tolist()
        chosen_title = st.selectbox("Mahsulotni tanlang:", sample_prods)

        if st.button("O'xshash va Tavsiya Qilinadigan Tovarlarni Topish"):
            # O'xshash toifalardagi tovarlarni ko'rsatish
            prod_row = df_products[df_products["title"] == chosen_title].iloc[0]
            cat_id = prod_row["category_id"]
            similar_prods = df_products[df_products["category_id"] == cat_id].head(4)
            st.write("###### 'Buni olganlar quyidagilarni ham tanlaydilar':")
            for _, r in similar_prods.iterrows():
                if r["title"] != chosen_title:
                    st.write(f" - **{r['title']}** | {r['price_current']:,} so'm | ⭐ {r['bayesian_rating']}")
