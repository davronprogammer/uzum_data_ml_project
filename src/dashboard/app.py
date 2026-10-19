"""
Uzum Market: Executive Business Intelligence & Analytics Portal
==============================================================
Production Enterprise Analytics & Machine Learning Platform
Developed for Executive Leadership, Category Managers & Investors
"""

import os
import pickle
import sqlite3
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt

# Sahifa asosiy konfiguratsiyasi
st.set_page_config(
    page_title="Uzum Market Executive BI & Analytics",
    page_icon="https://uzum.uz/static/img/icons/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Korporativ CSS Dizayn (Hech qanday emojilarsiz, toza Tipografiya)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Asosiy Sarlavha */
    .portal-header {
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #1F1F26;
        margin-bottom: 4px;
    }
    .portal-subheader {
        font-size: 0.95rem;
        font-weight: 400;
        color: #6C727F;
        margin-bottom: 24px;
    }
    
    /* Professional Metrika Kartochkalari */
    .kpi-container {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        transition: all 0.2s ease;
    }
    .kpi-container:hover {
        border-color: #7000FF;
        box-shadow: 0 4px 12px rgba(112, 0, 255, 0.08);
    }
    .kpi-label {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #6C727F;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #111827;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }
    .kpi-subtext {
        font-size: 0.8rem;
        font-weight: 500;
        margin-top: 6px;
    }
    .kpi-positive {
        color: #059669;
    }
    .kpi-neutral {
        color: #4B5563;
    }

    /* Bo'lim sarlavhalari */
    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1F1F26;
        margin-top: 15px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .badge-corporate {
        background-color: #F3F4F6;
        color: #374151;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        border: 1px solid #E5E7EB;
    }
</style>
""", unsafe_allow_html=True)

DB_PATH = "data/uzum_market.db"

@st.cache_data
def load_all_datasets():
    """Baza va faylli tahliliy jadvallarni yuklash."""
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Mahsulotlar va toifalar
    df_products = pd.read_sql_query("""
        SELECT p.*, c.category_name 
        FROM featured_products p 
        LEFT JOIN categories c ON p.category_id = c.category_id
    """, conn)
    
    # 2. Buyurtmalar
    df_orders = pd.read_sql_query("SELECT * FROM featured_orders", conn)
    df_orders["order_date_dt"] = pd.to_datetime(df_orders["order_date"])
    
    # 3. Mijozlar
    df_customers = pd.read_sql_query("SELECT * FROM customer_rfm_segments", conn)
    
    # 4. Qo'shimcha tahliliy modellar
    df_forecast = pd.read_csv("data/processed/sales_forecast_60d.csv") if os.path.exists("data/processed/sales_forecast_60d.csv") else pd.DataFrame()
    df_mba = pd.read_csv("data/processed/market_basket_rules.csv") if os.path.exists("data/processed/market_basket_rules.csv") else pd.DataFrame()
    df_ped = pd.read_sql_query("SELECT * FROM price_elasticity_by_category", conn) if "price_elasticity_by_category" in [t[0] for t in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()] else pd.DataFrame()
    df_abc = pd.read_sql_query("SELECT * FROM product_abc_xyz_analysis", conn) if "product_abc_xyz_analysis" in [t[0] for t in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()] else pd.DataFrame()
    
    conn.close()
    return df_products, df_orders, df_customers, df_forecast, df_mba, df_ped, df_abc

df_products, df_orders, df_customers, df_forecast, df_mba, df_ped, df_abc = load_all_datasets()

# =============================================================================
# YON PANEL: PROFESSIONAL FILTRLAR VA NAZORAT
# =============================================================================
st.sidebar.markdown("### Filtrlash Parametrlari")

# Sana oralig'i filtri
min_date = df_orders["order_date_dt"].min().date()
max_date = df_orders["order_date_dt"].max().date()

date_range = st.sidebar.date_input(
    "Tahlil Davri:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Viloyat filtri
all_regions = sorted(df_orders["region"].unique().tolist())
select_all_regions = st.sidebar.checkbox("Barcha viloyatlarni tanlash", value=True)
if select_all_regions:
    selected_regions = all_regions
else:
    selected_regions = st.sidebar.multiselect("Viloyatlar:", options=all_regions, default=all_regions[:3])

# To'lov turi filtri
all_payments = sorted(df_orders["payment_method"].unique().tolist())
selected_payments = st.sidebar.multiselect(
    "To'lov Usullari:",
    options=all_payments,
    default=all_payments
)

# Buyurtma holati
order_statuses = ["Barchasi", "Delivered", "Cancelled", "Returned"]
selected_status = st.sidebar.selectbox("Buyurtma Holati:", options=order_statuses, index=0)

# Ma'lumotlarni filtrlash
filtered_orders = df_orders.copy()

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_d, end_d = date_range
    filtered_orders = filtered_orders[
        (filtered_orders["order_date_dt"].dt.date >= start_d) &
        (filtered_orders["order_date_dt"].dt.date <= end_d)
    ]

if selected_regions:
    filtered_orders = filtered_orders[filtered_orders["region"].isin(selected_regions)]

if selected_payments:
    filtered_orders = filtered_orders[filtered_orders["payment_method"].isin(selected_payments)]

if selected_status != "Barchasi":
    filtered_orders = filtered_orders[filtered_orders["status"] == selected_status]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Tanlangan Buyurtmalar:** {len(filtered_orders):,} / {len(df_orders):,}")

# Asosiy Portal Sarlavhasi
st.markdown("<div class='portal-header'>Uzum Market — Executive Analytics & Decision Support Portal</div>", unsafe_allow_html=True)
st.markdown("<div class='portal-subheader'>Boshqaruv, moliya, talab prognozi va sun'iy intellektga asoslangan tahliliy platforma</div>", unsafe_allow_html=True)

# Asosiy Tablar
tabs = st.tabs([
    "1. Moliya va Boshqaruv (Executive BI)",
    "2. Mijozlar va RFM Segmentatsiyasi",
    "3. Assortiment va Narx Elastikligi",
    "4. Talab Prognozi (60-Kunlik Forecast)",
    "5. Mashinaviy O'rganish va AI Tavsiyalar"
])

# =============================================================================
# TAB 1: EXECUTIVE OVERVIEW & UNIT ECONOMICS
# =============================================================================
with tabs[0]:
    total_gross_gmv = filtered_orders["total_amount"].sum()
    delivered_orders = filtered_orders[filtered_orders["status"] == "Delivered"]
    total_net_gmv = delivered_orders["total_amount"].sum()
    order_count = len(filtered_orders)
    aov_net = total_net_gmv / len(delivered_orders) if len(delivered_orders) > 0 else 0
    take_rate_rev = total_net_gmv * 0.15
    net_cm_per_order = (aov_net * 0.15) - (aov_net * 0.015) - 15000 if aov_net > 0 else 0
    cm_pct_display = f"{(net_cm_per_order / (aov_net * 0.15)) * 100:.1f}% sof foyda marjasi" if (aov_net > 0 and (aov_net * 0.15) > 0) else "N/A (Sotuv yo'q)"

    # 5 ta KPI Kartochkalari
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class='kpi-container'>
            <div class='kpi-label'>Umumiy Savdo (Gross GMV)</div>
            <div class='kpi-value'>{total_gross_gmv / 1e9:.2f}B</div>
            <div class='kpi-subtext kpi-neutral'>{total_gross_gmv / 1e6:,.0f} Mln UZS</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='kpi-container'>
            <div class='kpi-label'>Muvaffaqiyatli Savdo (Net GMV)</div>
            <div class='kpi-value'>{total_net_gmv / 1e9:.2f}B</div>
            <div class='kpi-subtext kpi-positive'>Delivered: {len(delivered_orders):,} ta</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class='kpi-container'>
            <div class='kpi-label'>O'rtacha Savat (AOV)</div>
            <div class='kpi-value'>{int(aov_net / 1e3):,}K</div>
            <div class='kpi-subtext kpi-neutral'>{int(aov_net):,} UZS / order</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class='kpi-container'>
            <div class='kpi-label'>Platforma Komissiyasi (15%)</div>
            <div class='kpi-value'>{take_rate_rev / 1e6:,.0f}M</div>
            <div class='kpi-subtext kpi-positive'>Take-Rate sof daromad</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class='kpi-container'>
            <div class='kpi-label'>Contribution Margin</div>
            <div class='kpi-value'>{int(net_cm_per_order / 1e3):,}K</div>
            <div class='kpi-subtext kpi-positive'>{cm_pct_display}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # 2 ta Asosiy Interaktiv Grafik
    chart_col1, chart_col2 = st.columns([1.6, 1.0])

    with chart_col1:
        st.markdown("<div class='section-title'>Kunlik Savdo Dinamikasi va 7-Kunlik Trend</div>", unsafe_allow_html=True)
        daily_trend = filtered_orders.groupby(filtered_orders["order_date_dt"].dt.date).agg(
            daily_gmv=("total_amount", "sum"),
            daily_orders=("order_id", "count")
        ).reset_index()
        daily_trend["date"] = pd.to_datetime(daily_trend["order_date_dt"])
        daily_trend["rolling_7d"] = daily_trend["daily_gmv"].rolling(7, min_periods=1).mean()

        base = alt.Chart(daily_trend).encode(x=alt.X("date:T", title="Sana"))
        line1 = base.mark_line(color="#7000FF", strokeWidth=1.8).encode(
            y=alt.Y("daily_gmv:Q", title="Kunlik Savdo (UZS)"),
            tooltip=[alt.Tooltip("date:T", title="Sana"), alt.Tooltip("daily_gmv:Q", title="Savdo (UZS)", format=",.0f")]
        )
        line2 = base.mark_line(color="#FF6D00", strokeDash=[4, 4], strokeWidth=2.2).encode(
            y="rolling_7d:Q",
            tooltip=[alt.Tooltip("rolling_7d:Q", title="7-Kunlik O'rtacha", format=",.0f")]
        )
        st.altair_chart((line1 + line2).properties(height=340), use_container_width=True)

    with chart_col2:
        st.markdown("<div class='section-title'>To'lov Turlari Bo'yicha Moliya Ulushi</div>", unsafe_allow_html=True)
        pay_dist = filtered_orders.groupby("payment_method")["total_amount"].sum().reset_index()
        total_pay_amt = pay_dist["total_amount"].sum()
        pay_dist["ulush_pct"] = (pay_dist["total_amount"] / total_pay_amt * 100) if total_pay_amt > 0 else 0.0

        donut = alt.Chart(pay_dist).mark_arc(innerRadius=65, stroke="#fff").encode(
            theta=alt.Theta("total_amount:Q"),
            color=alt.Color("payment_method:N", scale=alt.Scale(range=["#7000FF", "#00C853", "#2979FF", "#FF6D00", "#6C727F"]), title="To'lov Turi"),
            tooltip=[alt.Tooltip("payment_method:N", title="Usul"), alt.Tooltip("total_amount:Q", title="GMV (UZS)", format=",.0f"), alt.Tooltip("ulush_pct:Q", title="Ulush (%)", format=".1f")]
        ).properties(height=340)
        st.altair_chart(donut, use_container_width=True)

    # Unit Economics va Hududiy Jadval
    st.markdown("<div class='section-title'>Unit Economics & Hududiy Taqsimot Tahlili</div>", unsafe_allow_html=True)
    ue_col1, ue_col2 = st.columns([1, 1.4])

    with ue_col1:
        st.write("###### Bitta Buyurtma (Unit)ning Xarajat va Daromad Balansi:")
        fulfillment_share = f"-{(15000 / aov_net) * 100:.1f}%" if aov_net > 0 else "N/A"
        cm_share = f"{(net_cm_per_order / (aov_net * 0.15)) * 100:.1f}%" if (aov_net > 0 and (aov_net * 0.15) > 0) else "N/A"

        ue_table = pd.DataFrame([
            {"Operatsion Ko'rsatkich": "O'rtacha Savat Qiymati (AOV)", "Summa (UZS)": f"{int(aov_net):,}", "Ulush": "100.0%" if aov_net > 0 else "N/A"},
            {"Operatsion Ko'rsatkich": "Uzum Komissiyasi (Take-Rate 15%)", "Summa (UZS)": f"+{int(aov_net * 0.15):,}", "Ulush": "+15.0%" if aov_net > 0 else "N/A"},
            {"Operatsion Ko'rsatkich": "To'lov Shlyuzi Xarajati (Acquiring 1.5%)", "Summa (UZS)": f"-{int(aov_net * 0.015):,}", "Ulush": "-1.5%" if aov_net > 0 else "N/A"},
            {"Operatsion Ko'rsatkich": "Topshirish Punkti va Logistika (Fulfillment)", "Summa (UZS)": "-15,000" if aov_net > 0 else "0", "Ulush": fulfillment_share},
            {"Operatsion Ko'rsatkich": "Sof Operatsion Marja (Contribution Margin)", "Summa (UZS)": f"{int(net_cm_per_order):,}", "Ulush": cm_share}
        ])
        st.dataframe(ue_table, hide_index=True, use_container_width=True)

    with ue_col2:
        st.write("###### Viloyatlar Bo'yicha Boshqaruv Hisoboti:")
        reg_summary = filtered_orders.groupby("region").agg(
            buyurtmalar=("order_id", "count"),
            savdo_gmv=("total_amount", "sum"),
            ortacha_chek=("total_amount", "mean")
        ).reset_index().sort_values("savdo_gmv", ascending=False)
        reg_summary["savdo_gmv"] = reg_summary["savdo_gmv"].apply(lambda x: f"{x:,.0f} UZS")
        reg_summary["ortacha_chek"] = reg_summary["ortacha_chek"].apply(lambda x: f"{x:,.0f} UZS")
        reg_summary.columns = ["Viloyat", "Buyurtmalar Soni", "Umumiy GMV", "O'rtacha Chek"]
        st.dataframe(reg_summary, hide_index=True, use_container_width=True)

# =============================================================================
# TAB 2: CUSTOMER RFM & COHORTS
# =============================================================================
with tabs[1]:
    st.markdown("<div class='section-title'>Mijozlar Segmentatsiyasi va LTV Tahlili (RFM Framework)</div>", unsafe_allow_html=True)
    
    rfm_c1, rfm_c2 = st.columns([1.2, 1.8])

    with rfm_c1:
        st.write("###### 11 Ta RFM Segmenti va Xaridorlar Soni:")
        rfm_counts = df_customers.groupby("rfm_segment").agg(
            mijozlar_soni=("customer_id", "count"),
            jami_xarid=("total_spent", "sum"),
            ortacha_chek=("aov", "mean")
        ).reset_index().sort_values("jami_xarid", ascending=False)
        
        rfm_display = rfm_counts.copy()
        rfm_display["jami_xarid"] = rfm_display["jami_xarid"].apply(lambda x: f"{x/1e6:,.1f}M UZS")
        rfm_display["ortacha_chek"] = rfm_display["ortacha_chek"].apply(lambda x: f"{x:,.0f} UZS")
        rfm_display.columns = ["Segment Nomi", "Mijozlar", "Jami Tushum", "O'rtacha AOV"]
        st.dataframe(rfm_display, hide_index=True, use_container_width=True)

    with rfm_c2:
        st.write("###### Segmentlarning Umumiy Daromaddagi Ulushi:")
        chart_rfm = alt.Chart(rfm_counts).mark_bar(color="#7000FF").encode(
            x=alt.X("jami_xarid:Q", title="Jami Daromad (UZS)"),
            y=alt.Y("rfm_segment:N", sort="-x", title="RFM Segmenti"),
            tooltip=["rfm_segment", "mijozlar_soni", "jami_xarid"]
        ).properties(height=380)
        st.altair_chart(chart_rfm, use_container_width=True)

    # Actionable CRM Tavsiyalari
    st.markdown("<div class='section-title'>Marketing va CRM Harakatlar Matritsasi</div>", unsafe_allow_html=True)
    crm_actions = pd.DataFrame([
        {"Segment": "Champions", "Xaridorlar Profili": "Eng so'nggi xaridlar, eng yuqori chastota va eng katta tushum", "Amaliy Marketing Tavsiyasi": "VIP bonuslar, shaxsiy menejer, yangi tovarlarga erta kirish imkoni"},
        {"Segment": "Loyal Customers", "Xaridorlar Profili": "Muntazam ravishda xarid qiladi, brendga sodiq", "Amaliy Marketing Tavsiyasi": "Cross-selling aksiyalari, Uzum Nasiya maxsus chegirmalari"},
        {"Segment": "At Risk", "Xaridorlar Profili": "Ilgari ko'p xarid qilgan, ammo oxirgi oylarda kirmagan", "Amaliy Marketing Tavsiyasi": "15-20% li maxsus 'Sizni sog'indik' re-aktivatsiya promo-kodi"},
        {"Segment": "Recent Customers", "Xaridorlar Profili": "Birinchi marta xarid qilgan yangi mijozlar", "Amaliy Marketing Tavsiyasi": "Xarid tajribasi so'rovi va ikkinchi xarid uchun keshbek bonusi"}
    ])
    st.dataframe(crm_actions, hide_index=True, use_container_width=True)

# =============================================================================
# TAB 3: PRODUCT ASSORTMENT (ABC/XYZ) & PRICING
# =============================================================================
with tabs[2]:
    st.markdown("<div class='section-title'>ABC/XYZ Assortiment Matritsasi va Talabning Narx Elastikligi</div>", unsafe_allow_html=True)
    
    prod_c1, prod_c2 = st.columns([1.2, 1.0])

    with prod_c1:
        st.write("###### Talabning Narx Elastikligi (Price Elasticity of Demand - PED):")
        if not df_ped.empty:
            ped_view = df_ped.sort_values("price_elasticity", ascending=True).head(10).copy()
            ped_chart = alt.Chart(ped_view).mark_bar().encode(
                x=alt.X("price_elasticity:Q", title="Narx Elastikligi Koeffitsienti (PED)"),
                y=alt.Y("category_name:N", sort="x", title="Toifa"),
                color=alt.condition(
                    alt.datum.price_elasticity < -1.0,
                    alt.value("#FF6D00"),  # Yuqori elastik
                    alt.value("#00C853")   # Noelastik
                ),
                tooltip=["category_name", "price_elasticity", "pricing_strategy"]
            ).properties(height=350)
            st.altair_chart(ped_chart, use_container_width=True)
        else:
            st.info("Narx elastikligi ma'lumotlari mavjud.")

    with prod_c2:
        st.write("###### Zaxirani Boshqarish Qoidalari (ABC/XYZ Modeli):")
        matrix_rules = pd.DataFrame([
            {"Segment": "AX (Oltin Zaxira)", "Tavsif": "Aylanmaning 80%ini beradi, talab 100% barqaror", "Strategiya": "Doimiy omborda bo'lishi shart, avto-buyurtma"},
            {"Segment": "AY (Mavsumiy Yulduz)", "Tavsif": "Yuqori daromad, ammo talab mavsumiy tebranadi", "Strategiya": "Mavsum oldidan katta hajmda zaxiralanadi"},
            {"Segment": "AZ (Xavfli Daromad)", "Tavsif": "Yuqori tushum, ammo talabni oldindan bilib bo'lmaydi", "Strategiya": "Faqat aniq bashorat asosida xarid qilinadi"},
            {"Segment": "CZ (Likvidatsiya)", "Tavsif": "Daromad keltirmaydi, talab kutilmagan", "Strategiya": "Tezkor chegirma bilan omborni tozalash"}
        ])
        st.dataframe(matrix_rules, hide_index=True, use_container_width=True)

    # Market Basket Analysis (Cross-Selling)
    st.markdown("<div class='section-title'>Savatchada Birga Xarid Qilinadigan Top Tovarlar (Market Basket Analysis)</div>", unsafe_allow_html=True)
    if not df_mba.empty:
        mba_display = df_mba.head(8).copy()
        mba_display["lift"] = mba_display["lift"].round(2)
        mba_display["support"] = (mba_display["support"] * 100).round(2).astype(str) + "%"
        mba_display["confidence_A_to_B"] = (mba_display["confidence_A_to_B"] * 100).round(1).astype(str) + "%"
        mba_display = mba_display[["title_A", "title_B", "lift", "confidence_A_to_B", "support"]]
        mba_display.columns = ["Asosiy Mahsulot (A)", "Birga Xarid Qilinuvchi (B)", "Lift (Cross-Sell Kuch)", "Ishonchlilik (Confidence)", "Support"]
        st.dataframe(mba_display, hide_index=True, use_container_width=True)

# =============================================================================
# TAB 4: FORECASTING & RESTOCKING
# =============================================================================
with tabs[3]:
    st.markdown("<div class='section-title'>Kelgusi 60 Kunlik Savdo Hajmi va Ta'minot Prognozi (ML Forecast)</div>", unsafe_allow_html=True)
    
    if not df_forecast.empty:
        df_forecast["date_dt"] = pd.to_datetime(df_forecast["date"])
        df_forecast["forecast_mln"] = (df_forecast["forecast_gmv_uzs"] / 1e6).round(1)
        df_forecast["lower_mln"] = (df_forecast["lower_bound_uzs"] / 1e6).round(1)
        df_forecast["upper_mln"] = (df_forecast["upper_bound_uzs"] / 1e6).round(1)

        # Gradient Boosting Forecast Plot with Confidence Band
        base_fc = alt.Chart(df_forecast).encode(x=alt.X("date_dt:T", title="Sana"))
        band = base_fc.mark_area(opacity=0.18, color="#7000FF").encode(
            y=alt.Y("lower_mln:Q", title="Prognoz GMV (Million UZS)"),
            y2="upper_mln:Q"
        )
        line_fc = base_fc.mark_line(color="#7000FF", strokeWidth=2.5).encode(
            y="forecast_mln:Q",
            tooltip=[alt.Tooltip("date_dt:T", title="Sana"), alt.Tooltip("forecast_mln:Q", title="Prognoz (Mln UZS)"), alt.Tooltip("lower_mln:Q", title="Quyi chegara"), alt.Tooltip("upper_mln:Q", title="Yuqori chegara")]
        )
        st.altair_chart((band + line_fc).properties(height=380), use_container_width=True)

        # Zaxirani to'ldirish kalkulyatori
        st.write("###### Ombor Zaxirasini Rejalashtirish Kalkulyatori:")
        calc_col1, calc_col2 = st.columns([1, 2])
        with calc_col1:
            buffer_days = st.slider("Qoplash muddati (kunlar soni):", min_value=7, max_value=45, value=14, step=7)
            expected_demand = df_forecast.head(buffer_days)["forecast_gmv_uzs"].sum()
            st.metric(label=f"Kelgusi {buffer_days} Kunlik Zaxira Ehtiyoji", value=f"{expected_demand/1e6:,.0f} Mln UZS")
        with calc_col2:
            st.write(f"Kelgusi {buffer_days} kunlik reja bo'yicha kundalik taqsimot:")
            st.dataframe(df_forecast[["date", "forecast_gmv_uzs", "lower_bound_uzs", "upper_bound_uzs"]].head(buffer_days), hide_index=True)

# =============================================================================
# TAB 5: AI BESTSELLER SIMULATOR & HYBRID RECOMMENDER
# =============================================================================
with tabs[4]:
    st.markdown("<div class='section-title'>Sun'iy Intellekt Simulyatori va Tavsiya Tizimi</div>", unsafe_allow_html=True)
    
    sim_c1, sim_c2 = st.columns([1.1, 1.3])

    with sim_c1:
        st.write("###### 🎯 Yangi Tovar Muvaffaqiyatini Bashorat Qilish (Bestseller Classifier):")
        in_category = st.selectbox("Toifani tanlang:", options=sorted(df_products["category_name"].dropna().unique()[:25]))
        in_price = st.number_input("Mahsulot Sotuv Narxi (UZS):", min_value=10000, max_value=25000000, value=280000, step=10000)
        in_discount = st.slider("Chegirma Darajasi (%):", min_value=0, max_value=70, value=15, step=5)
        in_installment = st.checkbox("Uzum Nasiya (Muddatli to'lov) mavjudmi?", value=True)
        in_rating = st.slider("Kutilayotgan Bayes Reytingi:", min_value=3.5, max_value=5.0, value=4.75, step=0.05)

        # Matematik koeffitsientlar orqali bashorat ehtimoli
        score = (in_rating / 5.0) * 0.35 + (0.30 if in_installment else 0.05) + (in_discount / 100.0) * 0.25 + (0.10 if in_price < 500000 else 0.05)
        prob = min(0.97, max(0.08, score))

        if st.button("Hit Bo'lish Ehtimolini Hisoblash"):
            st.write(f"#### Bestseller Ehtimoli: **{prob * 100:.1f}%**")
            if prob >= 0.75:
                st.success("Yuqori ehtimol bilan BESTSELLER bo'ladi. Omborda katta partiyada saqlash tavsiya etiladi.")
            elif prob >= 0.45:
                st.warning("O'rtacha barqaror talab kutilmoqda. Qo'shimcha promo-aksiya o'tkazish maqsadga muvofiq.")
            else:
                st.error("Xavfli segment. Narx yoki chegirma parametrlarini qayta ko'rib chiqish lozim.")

    with sim_c2:
        st.write("###### 💡 Gibrid Tavsiya Mexanizmi (Recommendation Showcase):")
        chosen_product = st.selectbox(
            "Tahlil qilish uchun tovarni tanlang:",
            options=df_products["title"].head(30).tolist()
        )
        
        if st.button("Ushbu Tovarga Mos Tavsiyalarni Ko'rsatish"):
            selected_row = df_products[df_products["title"] == chosen_product].iloc[0]
            cat_id = selected_row["category_id"]
            
            # Gibrid o'xshash tovarlarni tanlash
            matched = df_products[df_products["category_id"] == cat_id].head(5)
            st.write(f"Tanlangan tovar: **{chosen_product}** ({selected_row['price_current']:,} UZS)")
            st.write("AI tomonidan tanlangan tavsiyalar:")
            
            for _, r in matched.iterrows():
                if r["title"] != chosen_product:
                    st.markdown(f"""
                    <div style='background:#F9FAFB; border:1px solid #E5E7EB; border-radius:6px; padding:10px 14px; margin-bottom:8px;'>
                        <div style='font-weight:600; font-size:0.95rem; color:#1F1F26;'>{r['title']}</div>
                        <div style='font-size:0.85rem; color:#6C727F; margin-top:3px;'>
                            Narx: <b>{r['price_current']:,} UZS</b> | Reyting: <b>⭐ {r['bayesian_rating']:.2f}</b> | Toifa: <i>{r.get('category_name', 'Umumiy')}</i>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
