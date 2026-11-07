"""
E-Commerce Executive Analytics Dashboard (Streamlit Web App)
-----------------------------------------------------------
Interactive Business Intelligence Dashboard built with Streamlit & Plotly Express.
Executable directly on local browser or hosted on streamlit.io.
"""

from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & CORPORATE STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="E-Commerce Business Intelligence Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS styling for KPI Cards
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
    }
    .metric-title { font-size: 14px; color: #6c757d; font-weight: 600; }
    .metric-value { font-size: 24px; color: #1b365d; font-weight: 700; margin-top: 5px; }
    </style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 2. DATA LOADING ENGINE (CACHED FOR PERFORMANCE)
# -----------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed"


@st.cache_data(ttl=3600)
def load_data():
    """Loads processed datasets with automatic file existence validation."""
    master_file = PROCESSED_DATA_PATH / "master_order_items.parquet"
    if not master_file.exists():
        master_file = PROCESSED_DATA_PATH / "master_order_items.csv"

    orders_file = PROCESSED_DATA_PATH / "fact_orders.parquet"
    if not orders_file.exists():
        orders_file = PROCESSED_DATA_PATH / "fact_orders.csv"

    reviews_file = PROCESSED_DATA_PATH / "fact_order_reviews.parquet"
    if not reviews_file.exists():
        reviews_file = PROCESSED_DATA_PATH / "fact_order_reviews.csv"

    payments_file = PROCESSED_DATA_PATH / "fact_order_payments.parquet"
    if not payments_file.exists():
        payments_file = PROCESSED_DATA_PATH / "fact_order_payments.csv"

    df_master = (
        pd.read_parquet(master_file)
        if str(master_file).endswith(".parquet")
        else pd.read_csv(master_file)
    )
    df_orders = (
        pd.read_parquet(orders_file)
        if str(orders_file).endswith(".parquet")
        else pd.read_csv(orders_file)
    )
    df_reviews = (
        pd.read_parquet(reviews_file)
        if str(reviews_file).endswith(".parquet")
        else pd.read_csv(reviews_file)
    )
    df_payments = (
        pd.read_parquet(payments_file)
        if str(payments_file).endswith(".parquet")
        else pd.read_csv(payments_file)
    )

    return df_master, df_orders, df_reviews, df_payments


try:
    df_master, df_orders, df_reviews, df_payments = load_data()
except Exception as e:
    st.error(
        f"Data Loading Error: Run Day 4 transformations first to create processed datasets! Details: {str(e)}"
    )
    st.stop()

# Filter to delivered orders for gross revenue calculations
df_delivered_master = df_master[
    df_master["order_status"] == "delivered"
].copy()
df_delivered_orders = df_orders[
    df_orders["order_status"] == "delivered"
].copy()

# -----------------------------------------------------------------------------
# 3. INTERACTIVE SIDEBAR & NAVIGATION
# -----------------------------------------------------------------------------
st.sidebar.image(
    "https://cdn-icons-png.flaticon.com/512/3144/3144456.png", width=70
)
st.sidebar.title("E-Commerce BI Control")
st.sidebar.markdown("---")

# Navigation Menu
page = st.sidebar.radio(
    "Select Dashboard View:",
    [
        "📊 Executive Overview",
        "📦 Product Analytics",
        "👥 Customer RFM Behavior",
        "🚚 Logistics & Operations",
    ],
)

st.sidebar.markdown("---")
st.sidebar.subheader("Global Filters")

# Year Filter
available_years = sorted(
    df_delivered_orders["purchase_year"].dropna().unique().astype(int)
)
selected_years = st.sidebar.multiselect(
    "Select Year(s):", available_years, default=available_years
)

# State Filter
available_states = sorted(
    df_delivered_master["customer_state"].dropna().unique()
)
selected_states = st.sidebar.multiselect(
    "Select Customer State(s):", available_states, default=available_states
)

# Apply Global Filters
filtered_orders = df_delivered_orders[
    (df_delivered_orders["purchase_year"].isin(selected_years))
    & (df_delivered_orders["customer_state"].isin(selected_states))
]

filtered_master = df_delivered_master[
    (df_delivered_master["purchase_year"].isin(selected_years))
    & (df_delivered_master["customer_state"].isin(selected_states))
]

# -----------------------------------------------------------------------------
# PAGE 1: EXECUTIVE OVERVIEW
# -----------------------------------------------------------------------------
if page == "📊 Executive Overview":
    st.title("📊 Executive Performance Overview")
    st.markdown(
        "High-level commercial performance metrics, monthly GMV trends, and revenue composition."
    )
    st.markdown("---")

    # Key Metrics Calculation
    total_revenue = filtered_master["price"].sum()
    total_freight = filtered_master["freight_value"].sum()
    total_orders_cnt = filtered_orders["order_id"].nunique()
    total_customers_cnt = filtered_orders["customer_unique_id"].nunique()
    aov = total_revenue / total_orders_cnt if total_orders_cnt > 0 else 0
    avg_delivery_days = filtered_orders["actual_delivery_days"].mean()

    # Top KPI Cards Display
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric(
        label="Total Gross Revenue", value=f"R$ {total_revenue/1e6:,.2f}M"
    )
    kpi2.metric(label="Total Delivered Orders", value=f"{total_orders_cnt:,}")
    kpi3.metric(
        label="Unique Buyers", value=f"{total_customers_cnt:,}"
    )
    kpi4.metric(label="Average Order Value", value=f"R$ {aov:,.2f}")
    kpi5.metric(
        label="Avg Delivery Speed",
        value=f"{avg_delivery_days:.1f} Days"
        if not pd.isna(avg_delivery_days)
        else "N/A",
    )

    st.markdown("---")

    # Chart 1: Monthly Revenue Trend
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("Monthly Gross Revenue Trend (GMV)")
        monthly_rev = (
            filtered_master.groupby("purchase_year_month")["price"]
            .sum()
            .reset_index()
        )
        monthly_rev = monthly_rev[
            monthly_rev["purchase_year_month"] < "2018-09"
        ]  # Trim partial trailing month

        fig_trend = px.line(
            monthly_rev,
            x="purchase_year_month",
            y="price",
            markers=True,
            labels={
                "purchase_year_month": "Month (YYYY-MM)",
                "price": "Revenue (BRL)",
            },
            color_discrete_sequence=["#1b365d"],
        )
        fig_trend.update_layout(
            hovermode="x unified",
            xaxis_tickangle=-45,
            margin=dict(l=20, r=20, t=30, b=20),
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_right:
        st.subheader("Revenue Share by Payment Type")
        merged_pay = filtered_orders[["order_id"]].merge(
            df_payments, on="order_id", how="inner"
        )
        pay_summary = (
            merged_pay.groupby("payment_type")["payment_value"]
            .sum()
            .reset_index()
        )

        fig_donut = px.pie(
            pay_summary,
            names="payment_type",
            values="payment_value",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_donut.update_layout(margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_donut, use_container_width=True)

    # Chart 2: Top 10 Product Categories by Revenue
    st.subheader("Top 10 Revenue-Generating Product Categories")
    top_cat = (
        filtered_master.groupby("product_category_name_english")["price"]
        .sum()
        .reset_index()
        .sort_values(by="price", ascending=False)
        .head(10)
    )

    fig_cat = px.bar(
        top_cat,
        x="price",
        y="product_category_name_english",
        orientation="h",
        text_auto=".2s",
        labels={
            "price": "Revenue (BRL)",
            "product_category_name_english": "Category",
        },
        color="price",
        color_continuous_scale="Blues",
    )
    fig_cat.update_layout(
        yaxis={"categoryorder": "total ascending"},
        showlegend=False,
        margin=dict(l=20, r=20, t=30, b=20),
    )
    st.plotly_chart(fig_cat, use_container_width=True)

# -----------------------------------------------------------------------------
# PAGE 2: PRODUCT ANALYTICS
# -----------------------------------------------------------------------------
elif page == "📦 Product Analytics":
    st.title("📦 Product & Category Diagnostics")
    st.markdown(
        "Pareto 80/20 category distributions, pricing dynamics, and shipping freight friction."
    )
    st.markdown("---")

    # Pareto 80/20 Category Revenue Breakdown
    cat_summary = (
        filtered_master.groupby("product_category_name_english")
        .agg(
            total_revenue=("price", "sum"),
            items_sold=("order_item_id", "count"),
            avg_price=("price", "mean"),
            avg_freight=("freight_value", "mean"),
        )
        .reset_index()
        .sort_values(by="total_revenue", ascending=False)
    )

    total_platform_rev = cat_summary["total_revenue"].sum()
    cat_summary["cumulative_revenue"] = cat_summary["total_revenue"].cumsum()
    cat_summary["cumulative_share_pct"] = (
        cat_summary["cumulative_revenue"] / total_platform_rev
    ) * 100

    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("Pareto 80/20 Revenue Curve (Top 20 Categories)")
        top_20 = cat_summary.head(20)

        fig_pareto = go.Figure()
        fig_pareto.add_trace(
            go.Bar(
                x=top_20["product_category_name_english"],
                y=top_20["total_revenue"],
                name="Category Revenue (BRL)",
                marker_color="#2b5c8f",
            )
        )
        fig_pareto.add_trace(
            go.Scatter(
                x=top_20["product_category_name_english"],
                y=top_20["cumulative_share_pct"],
                name="Cumulative Revenue %",
                yaxis="y2",
                line=dict(color="#d9534f", width=2.5),
            )
        )
        fig_pareto.update_layout(
            yaxis=dict(title="Total Revenue (BRL)"),
            yaxis2=dict(
                title="Cumulative Share (%)", overlaying="y", side="right"
            ),
            xaxis_tickangle=-45,
            legend=dict(x=0.6, y=1.1, orientation="h"),
            margin=dict(l=20, r=20, t=30, b=20),
        )
        st.plotly_chart(fig_pareto, use_container_width=True)

    with col2:
        st.subheader("Shipping Friction (Freight-to-Price Ratio)")
        cat_summary["freight_ratio_pct"] = (
            cat_summary["avg_freight"] / cat_summary["avg_price"]
        ) * 100
        friction_df = cat_summary[cat_summary["items_sold"] >= 100].sort_values(
            by="freight_ratio_pct", ascending=False
        )

        fig_friction = px.scatter(
            friction_df.head(15),
            x="avg_price",
            y="freight_ratio_pct",
            size="items_sold",
            hover_name="product_category_name_english",
            color="freight_ratio_pct",
            color_continuous_scale="Reds",
            labels={
                "avg_price": "Avg Product Price (BRL)",
                "freight_ratio_pct": "Freight Ratio (%)",
            },
        )
        fig_friction.update_layout(margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_friction, use_container_width=True)

# -----------------------------------------------------------------------------
# PAGE 3: CUSTOMER RFM BEHAVIOR
# -----------------------------------------------------------------------------
elif page == "👥 Customer RFM Behavior":
    st.title("👥 Customer Behavioral & RFM Analytics")
    st.markdown(
        "Customer segmentation, repeat purchase analysis, and buyer cohort distributions."
    )
    st.markdown("---")

    # Repeat Purchase Rate Metrics
    cust_orders = (
        filtered_orders.groupby("customer_unique_id")["order_id"]
        .nunique()
        .reset_index()
    )
    total_buyers = len(cust_orders)
    repeat_buyers = (cust_orders["order_id"] > 1).sum()
    repeat_rate = (
        (repeat_buyers / total_buyers) * 100 if total_buyers > 0 else 0
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Unique Customers", f"{total_buyers:,}")
    c2.metric("Repeat Customers (>1 Order)", f"{repeat_buyers:,}")
    c3.metric("Repeat Purchase Rate", f"{repeat_rate:.2f}%")

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Order Frequency Distribution")
        freq_dist = (
            cust_orders["order_id"]
            .value_counts()
            .reset_index()
            .rename(
                columns={"order_id": "orders_made", "count": "customer_count"}
            )
        )

        fig_freq = px.bar(
            freq_dist,
            x="orders_made",
            y="customer_count",
            text="customer_count",
            labels={
                "orders_made": "Orders Placed per Customer",
                "customer_count": "Count of Customers",
            },
            color_discrete_sequence=["#00a896"],
        )
        st.plotly_chart(fig_freq, use_container_width=True)

    with col_b:
        st.subheader("State-Wise Unique Buyer Density")
        state_cust = (
            filtered_orders.groupby("customer_state")["customer_unique_id"]
            .nunique()
            .reset_index()
            .sort_values(by="customer_unique_id", ascending=False)
            .head(10)
        )

        fig_state = px.bar(
            state_cust,
            x="customer_unique_id",
            y="customer_state",
            orientation="h",
            color="customer_unique_id",
            color_continuous_scale="Viridis",
            labels={
                "customer_unique_id": "Unique Buyers",
                "customer_state": "State",
            },
        )
        fig_state.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_state, use_container_width=True)

# -----------------------------------------------------------------------------
# PAGE 4: LOGISTICS & OPERATIONS
# -----------------------------------------------------------------------------
elif page == "🚚 Logistics & Operations":
    st.title("🚚 Operational Logistics & Delivery Analytics")
    st.markdown(
        "Fulfillment timeliness, late delivery regional hotspots, and customer review impacts."
    )
    st.markdown("---")

    # Delivery Metrics
    late_orders_cnt = (filtered_orders["is_late_delivery"] == 1).sum()
    total_deliv = len(filtered_orders)
    late_rate = (late_orders_cnt / total_deliv) * 100 if total_deliv > 0 else 0

    merged_rev = filtered_orders[["order_id"]].merge(
        df_reviews, on="order_id", how="inner"
    )
    avg_review = merged_rev["review_score"].mean()

    m1, m2, m3 = st.columns(3)
    m1.metric(
        "Average Delivery Duration",
        f"{filtered_orders['actual_delivery_days'].mean():.1f} Days",
    )
    m2.metric(
        "Late Delivery Rate",
        f"{late_rate:.2f}%",
        delta=f"{late_orders_cnt:,} Orders Late",
        delta_color="inverse",
    )
    m3.metric(
        "Average Review Score",
        f"{avg_review:.2f} ⭐" if not pd.isna(avg_review) else "N/A",
    )

    st.markdown("---")

    col_x, col_y = st.columns(2)

    with col_x:
        st.subheader("Late Delivery Rate (%) by Customer State")
        state_late = (
            filtered_orders.groupby("customer_state")
            .agg(
                total_orders=("order_id", "count"),
                late_orders=("is_late_delivery", "sum"),
            )
            .reset_index()
        )
        state_late["late_rate_pct"] = (
            state_late["late_orders"] / state_late["total_orders"]
        ) * 100
        state_late = state_late[state_late["total_orders"] >= 100].sort_values(
            by="late_rate_pct", ascending=False
        )

        fig_late = px.bar(
            state_late.head(10),
            x="late_rate_pct",
            y="customer_state",
            orientation="h",
            color="late_rate_pct",
            color_continuous_scale="Reds",
            labels={
                "late_rate_pct": "Late Delivery Rate (%)",
                "customer_state": "State",
            },
        )
        fig_late.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_late, use_container_width=True)

    with col_y:
        st.subheader("Review Score Breakdown vs Shipping Delays")
        merged_deliv_rev = filtered_orders.merge(
            df_reviews, on="order_id", how="inner"
        )

        def delay_label(row):
            if row["delivery_delay_days"] > 0:
                return "Late Delivery (>0 Days Late)"
            elif row["delivery_delay_days"] >= -3:
                return "On-Time (0-3 Days Early)"
            else:
                return "Early Delivery (>3 Days Early)"

        merged_deliv_rev["delay_cat"] = merged_deliv_rev.apply(
            delay_label, axis=1
        )
        review_summary = (
            merged_deliv_rev.groupby("delay_cat")["review_score"]
            .mean()
            .reset_index()
        )

        fig_rev = px.bar(
            review_summary,
            x="delay_cat",
            y="review_score",
            color="review_score",
            color_continuous_scale="RdYlGn",
            labels={
                "delay_cat": "Delivery Timeliness Status",
                "review_score": "Average Review (1-5 Stars)",
            },
            text_auto=".2f",
        )
        fig_rev.update_layout(yaxis_range=[1, 5])
        st.plotly_chart(fig_rev, use_container_width=True)