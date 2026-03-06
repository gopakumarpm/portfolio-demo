"""
Portfolio Demo App — Gopakumar
Showcases: Data Analysis, Interactive Dashboards, Python Automation
Deploy on Streamlit Cloud and link in Upwork proposals.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Data Analytics Portfolio — Gopakumar",
    page_icon="📊",
    layout="wide",
)

# --- Sidebar Navigation ---
st.sidebar.title("Portfolio Demos")
demo = st.sidebar.radio(
    "Choose a demo:",
    ["Sales Dashboard", "Data Cleaner", "CSV Analyzer"],
    index=0,
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Built by **Gopakumar**")
st.sidebar.markdown("Python | Data Science | AI | Streamlit")
st.sidebar.markdown("[GitHub](https://github.com/) | [Upwork Profile](#)")


# --- Helper: Generate sample sales data ---
@st.cache_data
def generate_sales_data(n_rows=2000):
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=365, freq="D")
    regions = ["North America", "Europe", "Asia Pacific", "Latin America"]
    products = ["Software License", "Consulting", "Support Plan", "Training", "Custom Dev"]

    rows = []
    for _ in range(n_rows):
        date = np.random.choice(dates)
        region = np.random.choice(regions, p=[0.35, 0.30, 0.20, 0.15])
        product = np.random.choice(products, p=[0.30, 0.25, 0.20, 0.15, 0.10])

        base_price = {
            "Software License": 5000, "Consulting": 8000,
            "Support Plan": 2000, "Training": 3000, "Custom Dev": 15000,
        }[product]

        revenue = base_price * np.random.uniform(0.5, 2.0)
        quantity = np.random.randint(1, 10)

        rows.append({
            "Date": pd.Timestamp(date),
            "Region": region,
            "Product": product,
            "Revenue": round(revenue, 2),
            "Quantity": quantity,
            "Customer_ID": f"CUST-{np.random.randint(1000, 9999)}",
        })

    return pd.DataFrame(rows).sort_values("Date").reset_index(drop=True)


# ============================================================
# DEMO 1: Interactive Sales Dashboard
# ============================================================
if demo == "Sales Dashboard":
    st.title("Interactive Sales Dashboard")
    st.caption("A fully interactive dashboard built with Streamlit + Plotly. Filter by date, region, and product to explore the data.")

    df = generate_sales_data()

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        date_range = st.date_input(
            "Date Range",
            value=(df["Date"].min().date(), df["Date"].max().date()),
            min_value=df["Date"].min().date(),
            max_value=df["Date"].max().date(),
        )
    with col2:
        selected_regions = st.multiselect("Regions", df["Region"].unique(), default=df["Region"].unique())
    with col3:
        selected_products = st.multiselect("Products", df["Product"].unique(), default=df["Product"].unique())

    # Apply filters
    if isinstance(date_range, tuple) and len(date_range) == 2:
        mask = (
            (df["Date"].dt.date >= date_range[0])
            & (df["Date"].dt.date <= date_range[1])
            & (df["Region"].isin(selected_regions))
            & (df["Product"].isin(selected_products))
        )
        filtered = df[mask]
    else:
        filtered = df[df["Region"].isin(selected_regions) & df["Product"].isin(selected_products)]

    # KPI cards
    st.markdown("---")
    k1, k2, k3, k4 = st.columns(4)
    total_rev = filtered["Revenue"].sum()
    total_deals = len(filtered)
    avg_deal = filtered["Revenue"].mean() if len(filtered) > 0 else 0
    top_product = filtered.groupby("Product")["Revenue"].sum().idxmax() if len(filtered) > 0 else "N/A"

    k1.metric("Total Revenue", f"${total_rev:,.0f}")
    k2.metric("Total Deals", f"{total_deals:,}")
    k3.metric("Avg Deal Size", f"${avg_deal:,.0f}")
    k4.metric("Top Product", top_product)

    # Charts
    st.markdown("---")
    chart1, chart2 = st.columns(2)

    with chart1:
        monthly = filtered.groupby(filtered["Date"].dt.to_period("M"))["Revenue"].sum().reset_index()
        monthly["Date"] = monthly["Date"].dt.to_timestamp()
        fig1 = px.area(monthly, x="Date", y="Revenue", title="Monthly Revenue Trend",
                       color_discrete_sequence=["#636EFA"])
        fig1.update_layout(height=350)
        st.plotly_chart(fig1, use_container_width=True)

    with chart2:
        by_region = filtered.groupby("Region")["Revenue"].sum().reset_index()
        fig2 = px.pie(by_region, values="Revenue", names="Region", title="Revenue by Region",
                      color_discrete_sequence=px.colors.qualitative.Set2)
        fig2.update_layout(height=350)
        st.plotly_chart(fig2, use_container_width=True)

    chart3, chart4 = st.columns(2)

    with chart3:
        by_product = filtered.groupby("Product")["Revenue"].sum().reset_index().sort_values("Revenue", ascending=True)
        fig3 = px.bar(by_product, x="Revenue", y="Product", orientation="h",
                      title="Revenue by Product", color="Product",
                      color_discrete_sequence=px.colors.qualitative.Pastel)
        fig3.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    with chart4:
        daily = filtered.groupby([filtered["Date"].dt.to_period("M"), "Region"])["Revenue"].sum().reset_index()
        daily["Date"] = daily["Date"].dt.to_timestamp()
        fig4 = px.line(daily, x="Date", y="Revenue", color="Region",
                       title="Monthly Revenue by Region")
        fig4.update_layout(height=350)
        st.plotly_chart(fig4, use_container_width=True)

    # Raw data
    with st.expander("View Raw Data"):
        st.dataframe(filtered, use_container_width=True)
        csv = filtered.to_csv(index=False)
        st.download_button("Download CSV", csv, "sales_data.csv", "text/csv")


# ============================================================
# DEMO 2: Data Cleaner Tool
# ============================================================
elif demo == "Data Cleaner":
    st.title("Automated Data Cleaner")
    st.caption("Upload a messy CSV and get a cleaned version instantly. Demonstrates Python automation skills.")

    uploaded = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded is not None:
        raw = pd.read_csv(uploaded)
        st.subheader("Original Data")
        st.dataframe(raw.head(20), use_container_width=True)

        # Cleaning report
        st.subheader("Cleaning Report")
        report = {}
        report["Total Rows"] = len(raw)
        report["Total Columns"] = len(raw.columns)
        report["Duplicate Rows"] = raw.duplicated().sum()

        missing = raw.isnull().sum()
        missing_cols = missing[missing > 0]

        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Total Rows", report["Total Rows"])
            st.metric("Duplicate Rows Found", report["Duplicate Rows"])
        with col_b:
            st.metric("Total Columns", report["Total Columns"])
            st.metric("Columns with Missing Data", len(missing_cols))

        if len(missing_cols) > 0:
            st.markdown("**Missing values by column:**")
            miss_df = pd.DataFrame({"Column": missing_cols.index, "Missing Count": missing_cols.values,
                                     "% Missing": (missing_cols.values / len(raw) * 100).round(1)})
            st.dataframe(miss_df, use_container_width=True)

        # Cleaning options
        st.subheader("Cleaning Options")
        remove_dupes = st.checkbox("Remove duplicate rows", value=True)
        strip_whitespace = st.checkbox("Strip whitespace from text columns", value=True)
        fill_strategy = st.selectbox("Handle missing values", ["Keep as-is", "Drop rows with missing", "Fill numeric with median", "Fill with 'Unknown'"])

        if st.button("Clean Data", type="primary"):
            cleaned = raw.copy()

            if remove_dupes:
                before = len(cleaned)
                cleaned = cleaned.drop_duplicates()
                st.success(f"Removed {before - len(cleaned)} duplicate rows.")

            if strip_whitespace:
                text_cols = cleaned.select_dtypes(include=["object"]).columns
                for col in text_cols:
                    cleaned[col] = cleaned[col].str.strip()
                st.success(f"Stripped whitespace from {len(text_cols)} text columns.")

            if fill_strategy == "Drop rows with missing":
                before = len(cleaned)
                cleaned = cleaned.dropna()
                st.success(f"Dropped {before - len(cleaned)} rows with missing values.")
            elif fill_strategy == "Fill numeric with median":
                num_cols = cleaned.select_dtypes(include=["number"]).columns
                for col in num_cols:
                    cleaned[col] = cleaned[col].fillna(cleaned[col].median())
                st.success(f"Filled missing values in {len(num_cols)} numeric columns with median.")
            elif fill_strategy == "Fill with 'Unknown'":
                cleaned = cleaned.fillna("Unknown")
                st.success("Filled all missing values with 'Unknown'.")

            st.subheader("Cleaned Data")
            st.dataframe(cleaned.head(20), use_container_width=True)

            csv = cleaned.to_csv(index=False)
            st.download_button("Download Cleaned CSV", csv, "cleaned_data.csv", "text/csv", type="primary")

    else:
        st.info("Upload any CSV file to see the data cleaner in action. Try a file with duplicates, missing values, or messy formatting.")


# ============================================================
# DEMO 3: CSV Analyzer
# ============================================================
elif demo == "CSV Analyzer":
    st.title("Instant CSV Analyzer")
    st.caption("Upload any CSV and get automatic statistical analysis and visualizations.")

    uploaded = st.file_uploader("Upload a CSV file", type=["csv"], key="analyzer")

    if uploaded is not None:
        df = pd.read_csv(uploaded)

        st.subheader("Dataset Overview")
        c1, c2, c3 = st.columns(3)
        c1.metric("Rows", f"{len(df):,}")
        c2.metric("Columns", len(df.columns))
        c3.metric("Memory", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")

        # Column types
        st.subheader("Column Summary")
        col_info = pd.DataFrame({
            "Type": df.dtypes.astype(str),
            "Non-Null": df.count(),
            "Null": df.isnull().sum(),
            "Unique": df.nunique(),
        })
        st.dataframe(col_info, use_container_width=True)

        # Numeric stats
        num_cols = df.select_dtypes(include=["number"]).columns.tolist()
        cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

        if num_cols:
            st.subheader("Numeric Column Statistics")
            st.dataframe(df[num_cols].describe().round(2), use_container_width=True)

            st.subheader("Distributions")
            selected_num = st.selectbox("Select numeric column", num_cols)
            fig = px.histogram(df, x=selected_num, nbins=30, title=f"Distribution of {selected_num}",
                              color_discrete_sequence=["#636EFA"])
            st.plotly_chart(fig, use_container_width=True)

            if len(num_cols) >= 2:
                st.subheader("Correlation Heatmap")
                corr = df[num_cols].corr()
                fig_corr = px.imshow(corr, text_auto=".2f", title="Correlation Matrix",
                                     color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
                st.plotly_chart(fig_corr, use_container_width=True)

        if cat_cols:
            st.subheader("Categorical Columns")
            selected_cat = st.selectbox("Select categorical column", cat_cols)
            value_counts = df[selected_cat].value_counts().head(15)
            fig_cat = px.bar(x=value_counts.index, y=value_counts.values,
                            title=f"Top values in {selected_cat}",
                            labels={"x": selected_cat, "y": "Count"},
                            color_discrete_sequence=["#EF553B"])
            st.plotly_chart(fig_cat, use_container_width=True)

        # Raw data
        with st.expander("View Full Dataset"):
            st.dataframe(df, use_container_width=True)

    else:
        st.info("Upload any CSV file to get instant analysis — statistics, distributions, correlations, and more.")


# --- Footer ---
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#888; font-size:0.85em;'>"
    "Built with Streamlit + Plotly + Pandas | Portfolio Demo by Gopakumar"
    "</div>",
    unsafe_allow_html=True,
)
