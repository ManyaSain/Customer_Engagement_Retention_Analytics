import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Customer Engagement & Retention Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>

/* KPI hover effect */
div[data-testid="stMetric"] {
    transition: all 0.25s ease-in-out;
}

/* When mouse moves over KPI */
div[data-testid="stMetric"]:hover {
    border: 1px solid #A78BFA !important;
    box-shadow: 0 0 18px rgba(167, 139, 250, 0.35);
    transform: translateY(-4px);
    background-color: #17152A !important;
    border-radius: 12px;
}

/* KPI label */
div[data-testid="stMetric"] label {
    color: #D8D1E8 !important;
}

/* KPI value */
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #F5F3FF !important;
}

</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("European_Bank_Cleaned.csv")

    numeric_cols = [
        "Year", "CustomerId", "CreditScore", "Age", "Tenure",
        "Balance", "NumOfProducts", "HasCrCard",
        "IsActiveMember", "EstimatedSalary", "Exited"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["Geography", "Gender", "Surname"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    return df


try:
    df = load_data()
except FileNotFoundError:
    st.error(
        "European_Bank_Cleaned.csv was not found. "
        "Keep the CSV file in the same folder as app.py."
    )
    st.stop()

required_columns = [
    "CustomerId", "Surname", "CreditScore", "Geography", "Gender",
    "Age", "Tenure", "Balance", "NumOfProducts", "HasCrCard",
    "IsActiveMember", "EstimatedSalary", "Exited"
]

missing_columns = [c for c in required_columns if c not in df.columns]

if missing_columns:
    st.error(f"Missing columns in the CSV: {', '.join(missing_columns)}")
    st.stop()

df["Churn Status"] = df["Exited"].map({0: "Retained", 1: "Churned"})
df["Activity Status"] = df["IsActiveMember"].map({
    0: "Inactive",
    1: "Active"
})
df["Credit Card Status"] = df["HasCrCard"].map({
    0: "No Credit Card",
    1: "Has Credit Card"
})

def engagement_profile(row):
    if row["IsActiveMember"] == 1 and row["NumOfProducts"] >= 2:
        return "Active Engaged"
    if row["IsActiveMember"] == 0 and row["Balance"] >= 100000:
        return "Inactive High-Balance"
    if row["IsActiveMember"] == 0:
        return "Inactive Disengaged"
    return "Active Low-Product"

df["Engagement Profile"] = df.apply(engagement_profile, axis=1)

df["Balance Segment"] = pd.cut(
    df["Balance"],
    bins=[-1, 50000, 100000, 150000, float("inf")],
    labels=["< €50K", "€50K–€100K", "€100K–€150K", "€150K+"]
)

df["Salary Segment"] = pd.cut(
    df["EstimatedSalary"],
    bins=[-1, 50000, 100000, 150000, float("inf")],
    labels=["< €50K", "€50K–€100K", "€100K–€150K", "€150K+"]
)

df["Relationship Strength"] = (
    (df["IsActiveMember"] * 50)
    + ((df["NumOfProducts"].clip(upper=4) / 4) * 50)
)

df["Relationship Tier"] = pd.cut(
    df["Relationship Strength"],
    bins=[-1, 25, 50, 75, 100],
    labels=["Low", "Moderate", "Strong", "Very Strong"]
)

def pct(value):
    return f"{value:.2f}%"

def safe_rate(numerator, denominator):
    if denominator == 0:
        return 0.0
    return (numerator / denominator) * 100

def churn_rate(data):
    if len(data) == 0:
        return 0.0
    return data["Exited"].mean() * 100

def retention_rate(data):
    if len(data) == 0:
        return 0.0
    return (1 - data["Exited"].mean()) * 100

def money(value):
    return f"€{value:,.0f}"

def chart_layout(fig, height=430):
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=65, b=20),

        font=dict(
            family="Arial",
            size=13,
            color="#E9D5FF"
        ),

        title_font=dict(
            size=20,
            color="#E9D5FF"
        ),

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend_title_text="",

        hoverlabel=dict(
            bgcolor="white",
            font_size=13,
            font_color="#24154F"
        )
    )

    fig.update_traces(
        textfont=dict(
            color="#E9D5FF",
            size=13
        )
    )

    return fig

def show_chart_note(what, why, insight):
    st.info(
        f"**What this shows:** {what}\n\n"
        f"**Why it matters:** {why}\n\n"
        f"**Key insight:** {insight}"
    )

st.sidebar.title("Dashboard Filters")
st.sidebar.caption("Select filters to explore customer segments.")

geo_options = sorted(
    df["Geography"].dropna().unique().tolist()
)

selected_geo = st.sidebar.selectbox(
    "Geography",
    options=["All"] + geo_options,
    index=0
)

gender_options = sorted(
    df["Gender"].dropna().unique().tolist()
)

selected_gender = st.sidebar.selectbox(
    "Gender",
    options=["All"] + gender_options,
    index=0
)

product_min, product_max = st.sidebar.slider(
    "Number of Products",
    min_value=int(df["NumOfProducts"].min()),
    max_value=int(df["NumOfProducts"].max()),
    value=(
        int(df["NumOfProducts"].min()),
        int(df["NumOfProducts"].max())
    )
)

balance_min, balance_max = st.sidebar.slider(
    "Balance Range",
    min_value=float(df["Balance"].min()),
    max_value=float(df["Balance"].max()),
    value=(
        float(df["Balance"].min()),
        float(df["Balance"].max())
    ),
    step=5000.0,
    format="€%.0f"
)

salary_min, salary_max = st.sidebar.slider(
    "Salary Range",
    min_value=float(df["EstimatedSalary"].min()),
    max_value=float(df["EstimatedSalary"].max()),
    value=(
        float(df["EstimatedSalary"].min()),
        float(df["EstimatedSalary"].max())
    ),
    step=5000.0,
    format="€%.0f"
)

activity_filter = st.sidebar.selectbox(
    "Engagement Status",
    options=["All", "Active", "Inactive"],
    index=0
)

churn_filter = st.sidebar.selectbox(
    "Customer Status",
    options=["All", "Retained", "Churned"],
    index=0
)

filtered = df.copy()

if selected_geo != "All":
    filtered = filtered[
        filtered["Geography"] == selected_geo
    ]

if selected_gender != "All":
    filtered = filtered[
        filtered["Gender"] == selected_gender
    ]

filtered = filtered[
    filtered["NumOfProducts"].between(
        product_min,
        product_max
    )
]

filtered = filtered[
    filtered["Balance"].between(
        balance_min,
        balance_max
    )
]

filtered = filtered[
    filtered["EstimatedSalary"].between(
        salary_min,
        salary_max
    )
]

if activity_filter != "All":
    filtered = filtered[
        filtered["Activity Status"] == activity_filter
    ]

if churn_filter != "All":
    filtered = filtered[
        filtered["Churn Status"] == churn_filter
    ]

st.sidebar.divider()

st.sidebar.metric(
    "Customers in View",
    f"{len(filtered):,}"
)

st.sidebar.caption(
    "Filters are optional. Select any filter to explore the data."
)

st.title("📊 Customer Engagement & Product Utilization Analytics")
st.subheader("Retention Strategy Dashboard")
st.caption(
    "Behavioral Analytics • Product Utilization • Customer Churn Risk • "
    "Unified Mentor Data Analytics Internship"
)

st.divider()

if filtered.empty:
    st.warning(
        "No customers match the selected filters. "
        "Please widen the filters from the sidebar."
    )
    st.stop()

st.header("📊 Executive Overview")
st.caption(
    "A high-level view of customer scale, churn, engagement and relationship depth."
)

total_customers = len(filtered)
churned_customers = int(filtered["Exited"].sum())
current_churn = churn_rate(filtered)
active_pct = filtered["IsActiveMember"].mean() * 100
avg_products = filtered["NumOfProducts"].mean()
avg_balance = filtered["Balance"].mean()

kpi_cols = st.columns(6)

with kpi_cols[0]:
    with st.container(border=True):
        st.metric("Total Customers", f"{total_customers:,}")
        with st.popover("🔎 Details"):
            st.write("Number of customers in the current filtered population.")
            st.write("Use the sidebar filters to change the population.")

with kpi_cols[1]:
    with st.container(border=True):
        st.metric("Churned Customers", f"{churned_customers:,}")
        with st.popover("🔎 Details"):
            st.write("Customers whose Exited value is 1.")
            st.write(f"Current churn rate: {pct(current_churn)}")

with kpi_cols[2]:
    with st.container(border=True):
        st.metric("Churn Rate", pct(current_churn))
        with st.popover("🔎 Details"):
            st.write("Churned customers divided by total customers.")
            st.write("Lower churn indicates a larger retained customer base.")

with kpi_cols[3]:
    with st.container(border=True):
        st.metric("Active Customers", pct(active_pct))
        with st.popover("🔎 Details"):
            st.write("Percentage of customers with IsActiveMember = 1.")
            st.write("This is the primary behavioral engagement indicator.")

with kpi_cols[4]:
    with st.container(border=True):
        st.metric("Avg. Products", f"{avg_products:.2f}")
        with st.popover("🔎 Details"):
            st.write("Average number of products held per customer.")
            st.write("It is used to study relationship depth and retention.")

with kpi_cols[5]:
    with st.container(border=True):
        st.metric("Avg. Balance", money(avg_balance))
        with st.popover("🔎 Details"):
            st.write("Average account balance in the current filtered population.")
            st.write("High balance alone does not necessarily indicate engagement.")

st.header("🎯 Required Retention KPIs")
st.caption("These KPIs directly map to the project objectives.")

active_df = filtered[filtered["IsActiveMember"] == 1]
inactive_df = filtered[filtered["IsActiveMember"] == 0]

active_retention = retention_rate(active_df)
inactive_retention = retention_rate(inactive_df)

engagement_retention_ratio = (
    active_retention / inactive_retention
    if inactive_retention > 0 else 0
)

retained_df = filtered[filtered["Exited"] == 0]
retained_avg_products = (
    retained_df["NumOfProducts"].mean()
    if len(retained_df) > 0 else 0
)

product_depth_index = (
    retained_avg_products / avg_products * 100
    if avg_products > 0 else 0
)

high_balance_df = filtered[filtered["Balance"] >= 100000]
high_balance_disengagement_rate = safe_rate(
    int((high_balance_df["IsActiveMember"] == 0).sum()),
    len(high_balance_df)
)

card_df = filtered[filtered["HasCrCard"] == 1]
no_card_df = filtered[filtered["HasCrCard"] == 0]

card_retention = retention_rate(card_df)
no_card_retention = retention_rate(no_card_df)
credit_card_stickiness = card_retention - no_card_retention

relationship_strength_index = filtered["Relationship Strength"].mean()

req_cols = st.columns(5)

with req_cols[0]:
    with st.container(border=True):
        st.metric(
            "Engagement Retention Ratio",
            f"{engagement_retention_ratio:.2f}×"
        )
        with st.popover("🔎 KPI meaning"):
            st.write(
                "Active-customer retention rate divided by "
                "inactive-customer retention rate."
            )
            st.write(
                f"Active retention: {pct(active_retention)} | "
                f"Inactive retention: {pct(inactive_retention)}"
            )

with req_cols[1]:
    with st.container(border=True):
        st.metric("Product Depth Index", f"{product_depth_index:.1f}")
        with st.popover("🔎 KPI meaning"):
            st.write(
                "Retained customers' average product count divided by "
                "the overall average product count × 100."
            )
            st.write(
                f"Retained average products: {retained_avg_products:.2f}"
            )

with req_cols[2]:
    with st.container(border=True):
        st.metric(
            "High-Balance Disengagement",
            pct(high_balance_disengagement_rate)
        )
        with st.popover("🔎 KPI meaning"):
            st.write(
                "Percentage of customers with balance ≥ €100,000 "
                "who are inactive."
            )
            st.write(f"High-balance customers: {len(high_balance_df):,}")

with req_cols[3]:
    with st.container(border=True):
        st.metric(
            "Credit Card Stickiness",
            f"{credit_card_stickiness:+.2f} pp"
        )
        with st.popover("🔎 KPI meaning"):
            st.write(
                "Retention rate of credit-card holders minus the "
                "retention rate of non-card holders."
            )
            st.write(
                f"Card holders: {pct(card_retention)} | "
                f"Non-card: {pct(no_card_retention)}"
            )

with req_cols[4]:
    with st.container(border=True):
        st.metric(
            "Relationship Strength Index",
            f"{relationship_strength_index:.1f}/100"
        )
        with st.popover("🔎 KPI meaning"):
            st.write(
                "Combined score using activity and product depth. "
                "Active status contributes 50 points and product depth "
                "contributes up to 50 points."
            )

st.header("🎯 Customer Retention Snapshot")

retained_count = int((filtered["Exited"] == 0).sum())
churned_count = int((filtered["Exited"] == 1).sum())

snapshot = pd.DataFrame({
    "Status": ["Retained", "Churned"],
    "Customers": [retained_count, churned_count]
})

fig_snapshot = px.pie(
    snapshot,
    names="Status",
    values="Customers",
    hole=0.58,
    title="Retained vs Churned Customers",
    color="Status",
    color_discrete_map={
        "Retained": "#8B5CF6",
        "Churned": "#0F172A"
    }
)
fig_snapshot.update_traces(
    textposition="inside",
    textinfo="label+percent"
)
chart_layout(fig_snapshot, 440)
st.plotly_chart(fig_snapshot, use_container_width=True)

show_chart_note(
    "The donut separates the filtered customer population into retained and churned customers.",
    "It gives an immediate view of the size of the retention challenge.",
    "The current filtered population contains {churned_count:,} churned customers, representing a churn rate of {pct(current_churn)}."
)

tabs = st.tabs([
    "📈 Engagement",
    "📦 Product Utilization",
    "💰 Financial Commitment",
    "💳 Credit Card",
    "⭐ Retention Strength",
    "🚨 Risk Detector",
    "🔍 Customer Explorer"
])

with tabs[0]:
    st.header("📈 Engagement vs Churn Overview")
    st.caption(
        "Tests whether customer activity is associated with stronger retention."
    )

    profile_summary = (
        filtered.groupby("Engagement Profile", as_index=False)
        .agg(
            Customers=("CustomerId", "count"),
            Churn_Rate=("Exited", "mean")
        )
    )
    profile_summary["Churn_Rate"] *= 100
    profile_summary = profile_summary.sort_values("Customers", ascending=False)

    c1, c2 = st.columns(2)

    with c1:
        fig_profile = px.bar(
            profile_summary,
            x="Engagement Profile",
            y="Customers",
            title="Customer Distribution by Engagement Profile",
            text="Customers",
            color="Engagement Profile",
            color_discrete_sequence=[
                "#7C3AED", "#14B8A6", "#6366F1", "#334155"
            ]
        )
        fig_profile.update_traces(textposition="outside")
        chart_layout(fig_profile, 430)
        st.plotly_chart(fig_profile, use_container_width=True)

        largest_profile = (
            profile_summary.iloc[0]["Engagement Profile"]
            if len(profile_summary) else "N/A"
        )
        largest_count = (
            int(profile_summary.iloc[0]["Customers"])
            if len(profile_summary) else 0
        )

        show_chart_note(
            "Customers are classified using activity status and product depth.",
            "The segmentation distinguishes engaged customers from inactive or shallow relationships.",
            f"The largest profile in the current filtered population is {largest_profile}, with {largest_count:,} customers."
        )

    with c2:
        fig_profile_churn = px.bar(
            profile_summary.sort_values("Churn_Rate", ascending=False),
            x="Engagement Profile",
            y="Churn_Rate",
            title="Churn Rate by Engagement Profile",
            text=profile_summary.sort_values(
                "Churn_Rate", ascending=False
            )["Churn_Rate"].round(1),
            color="Churn_Rate",
            color_continuous_scale=["#DDD6FE", "#7C3AED", "#24154F"]
        )
        fig_profile_churn.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )
        fig_profile_churn.update_yaxes(ticksuffix="%")
        chart_layout(fig_profile_churn, 430)
        st.plotly_chart(fig_profile_churn, use_container_width=True)

        highest_profile = profile_summary.sort_values(
            "Churn_Rate", ascending=False
        ).iloc[0]
        show_chart_note(
            "The chart compares churn rates across behavioral engagement profiles.",
            "Comparing profiles helps identify groups where retention interventions may be relevant.",
            f"{highest_profile['Engagement Profile']} has the highest observed churn rate at {highest_profile['Churn_Rate']:.2f}%."
        )

    active_inactive = pd.DataFrame({
        "Activity": ["Active", "Inactive"],
        "Retention Rate": [active_retention, inactive_retention]
    })

    fig_activity = px.line(
        active_inactive,
        x="Activity",
        y="Retention Rate",
        markers=True,
        text="Retention Rate",
        title="Retention Rate: Active vs Inactive Customers"
    )
    fig_activity.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="top center",
        line_width=4,
        marker_size=11
    )
    fig_activity.update_yaxes(ticksuffix="%")
    chart_layout(fig_activity, 420)
    st.plotly_chart(fig_activity, use_container_width=True)

    retention_gap = active_retention - inactive_retention

    show_chart_note(
        "The line chart compares retention rates for active and inactive customers.",
        "This directly tests whether engagement is associated with stronger customer retention.",
        f"Active customers have a retention rate {retention_gap:.2f} percentage points higher than inactive customers in the current filtered population."
    )

with tabs[1]:
    st.header("📦 Product Utilization Impact")
    st.caption(
        "Measures whether relationship depth and product adoption are associated with churn."
    )

    product_summary = (
        filtered.groupby("NumOfProducts", as_index=False)
        .agg(
            Customers=("CustomerId", "count"),
            Churn_Rate=("Exited", "mean"),
            Retention_Rate=("Exited", lambda x: (1 - x.mean()) * 100)
        )
    )
    product_summary["Churn_Rate"] *= 100

    c1, c2 = st.columns(2)

    with c1:
        fig_product_churn = px.line(
            product_summary,
            x="NumOfProducts",
            y="Churn_Rate",
            markers=True,
            text="Churn_Rate",
            title="Churn Rate by Number of Products"
        )
        fig_product_churn.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="top center",
            line_width=4,
            marker_size=10
        )
        fig_product_churn.update_xaxes(dtick=1)
        fig_product_churn.update_yaxes(ticksuffix="%")
        chart_layout(fig_product_churn, 430)
        st.plotly_chart(fig_product_churn, use_container_width=True)

        highest_product_churn = product_summary.loc[
            product_summary["Churn_Rate"].idxmax()
        ]

        show_chart_note(
            "This line chart shows how churn changes as the number of products increases.",
            "Product depth is one of the core project questions because broader relationships may behave differently from single-product relationships.",
            f"The highest observed churn rate is {highest_product_churn['Churn_Rate']:.2f}% for customers with {int(highest_product_churn['NumOfProducts'])} product(s)."
        )

    with c2:
        fig_product_retention = px.bar(
            product_summary,
            x="NumOfProducts",
            y="Retention_Rate",
            text="Retention_Rate",
            title="Retention Rate by Product Depth",
            color="Retention_Rate",
            color_continuous_scale=["#DDD6FE", "#14B8A6", "#24154F"]
        )
        fig_product_retention.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )
        fig_product_retention.update_xaxes(dtick=1)
        fig_product_retention.update_yaxes(ticksuffix="%")
        chart_layout(fig_product_retention, 430)
        st.plotly_chart(fig_product_retention, use_container_width=True)

        best_product_retention = product_summary.loc[
            product_summary["Retention_Rate"].idxmax()
        ]

        show_chart_note(
            "This chart compares customer retention across product-count groups.",
            "It helps evaluate whether deeper product relationships correspond with stronger loyalty.",
            f"The highest observed retention rate is {best_product_retention['Retention_Rate']:.2f}% for {int(best_product_retention['NumOfProducts'])} product(s)."
        )

    st.subheader("🔎 Product Depth Summary")
    st.dataframe(
        product_summary.style.format({
            "Churn_Rate": "{:.2f}%",
            "Retention_Rate": "{:.2f}%"
        }),
        use_container_width=True,
        hide_index=True
    )

with tabs[2]:
    st.header("💰 Financial Commitment vs Engagement")
    st.caption(
        "Identifies financially valuable customers whose engagement may be weaker."
    )

    c1, c2 = st.columns(2)

    with c1:
        scatter_sample = filtered.sample(
            min(len(filtered), 2500),
            random_state=42
        )

        fig_balance_activity = px.scatter(
            scatter_sample,
            x="Balance",
            y="EstimatedSalary",
            color="Activity Status",
            symbol="Churn Status",
            hover_data=[
                "CustomerId",
                "Geography",
                "NumOfProducts",
                "CreditScore"
            ],
            title="Balance vs Estimated Salary by Engagement",
            color_discrete_map={
                "Active": "#14B8A6",
                "Inactive": "#7C3AED"
            }
        )
        fig_balance_activity.update_xaxes(tickprefix="€")
        fig_balance_activity.update_yaxes(tickprefix="€")
        chart_layout(fig_balance_activity, 470)
        st.plotly_chart(fig_balance_activity, use_container_width=True)

        show_chart_note(
            "Each point represents a customer, comparing balance and estimated salary while showing activity and churn status.",
            "A high balance does not automatically mean strong engagement, so the two dimensions should be viewed together.",
            "The highlighted inactive high-balance customers are the primary premium-risk segment monitored by this project."
        )

    with c2:
        balance_summary = (
            filtered.groupby("Balance Segment", observed=False, as_index=False)
            .agg(
                Customers=("CustomerId", "count"),
                Churn_Rate=("Exited", "mean")
            )
        )
        balance_summary["Churn_Rate"] *= 100

        fig_balance_churn = px.bar(
            balance_summary,
            x="Balance Segment",
            y="Churn_Rate",
            text="Churn_Rate",
            title="Churn Rate by Balance Segment",
            color="Churn_Rate",
            color_continuous_scale=["#DDD6FE", "#7C3AED", "#24154F"]
        )
        fig_balance_churn.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )
        fig_balance_churn.update_yaxes(ticksuffix="%")
        chart_layout(fig_balance_churn, 470)
        st.plotly_chart(fig_balance_churn, use_container_width=True)

        max_balance_churn = balance_summary.loc[
            balance_summary["Churn_Rate"].idxmax()
        ]

        show_chart_note(
            "Customers are grouped into balance bands and their churn rates are compared.",
            "This tests whether financial value and retention move together across the customer base.",
            f"The highest observed churn rate occurs in the {max_balance_churn['Balance Segment']} balance segment at {max_balance_churn['Churn_Rate']:.2f}%."
        )

    st.subheader("💎 High-Balance Disengagement Monitor")

    high_balance_inactive = filtered[
        (filtered["Balance"] >= 100000)
        & (filtered["IsActiveMember"] == 0)
    ]

    st.metric(
        "Inactive Customers with Balance ≥ €100,000",
        f"{len(high_balance_inactive):,}"
    )

    show_chart_note(
        "This count identifies customers with substantial balances who are currently inactive.",
        "It directly addresses the requirement to detect disengaged but financially valuable customers.",
        f"{len(high_balance_inactive):,} customers meet the €100,000 high-balance and inactive criteria in the current filter view."
    )

with tabs[3]:
    st.header("💳 Credit Card Stickiness")
    st.caption(
        "Examines whether credit-card ownership is associated with customer retention."
    )

    card_summary = (
        filtered.groupby("Credit Card Status", as_index=False)
        .agg(
            Customers=("CustomerId", "count"),
            Retention_Rate=("Exited", lambda x: (1 - x.mean()) * 100),
            Churn_Rate=("Exited", lambda x: x.mean() * 100)
        )
    )

    c1, c2 = st.columns(2)

    with c1:
        fig_card_retention = px.bar(
            card_summary,
            x="Credit Card Status",
            y="Retention_Rate",
            text="Retention_Rate",
            title="Retention Rate by Credit Card Ownership",
            color="Credit Card Status",
            color_discrete_sequence=["#14B8A6", "#7C3AED"]
        )
        fig_card_retention.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )
        fig_card_retention.update_yaxes(ticksuffix="%")
        chart_layout(fig_card_retention, 430)
        st.plotly_chart(fig_card_retention, use_container_width=True)

        show_chart_note(
            "The chart compares retention between credit-card holders and non-holders.",
            "Credit-card ownership is one of the behavioral/product indicators specified in the project requirements.",
            f"Credit-card holders show a retention rate of {pct(card_retention)}, compared with {pct(no_card_retention)} for non-card customers."
        )

    with c2:
        fig_card_churn = px.line(
            card_summary,
            x="Credit Card Status",
            y="Churn_Rate",
            markers=True,
            text="Churn_Rate",
            title="Churn Rate by Credit Card Ownership"
        )
        fig_card_churn.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="top center",
            line_width=4,
            marker_size=11
        )
        fig_card_churn.update_yaxes(ticksuffix="%")
        chart_layout(fig_card_churn, 430)
        st.plotly_chart(fig_card_churn, use_container_width=True)

        show_chart_note(
            "This line view shows the churn-rate difference between the two credit-card groups.",
            "It provides the churn-side interpretation of the credit-card stickiness KPI.",
            f"The current credit-card stickiness score is {credit_card_stickiness:+.2f} percentage points."
        )

with tabs[4]:
    st.header("⭐ Retention Strength Analysis")
    st.caption(
        "Combines engagement and product depth into a transparent relationship score."
    )

    strength_summary = (
        filtered.groupby("Relationship Tier", observed=False, as_index=False)
        .agg(
            Customers=("CustomerId", "count"),
            Churn_Rate=("Exited", "mean")
        )
    )
    strength_summary["Churn_Rate"] *= 100

    c1, c2 = st.columns(2)

    with c1:
        fig_strength_distribution = px.bar(
            strength_summary,
            x="Relationship Tier",
            y="Customers",
            text="Customers",
            title="Customer Distribution by Relationship Strength",
            color="Relationship Tier",
            color_discrete_sequence=[
                "#CBD5E1", "#A78BFA", "#14B8A6", "#24154F"
            ]
        )
        fig_strength_distribution.update_traces(
            textposition="outside"
        )
        chart_layout(fig_strength_distribution, 430)
        st.plotly_chart(
            fig_strength_distribution,
            use_container_width=True
        )

        show_chart_note(
            "Customers are grouped into relationship-strength tiers based on activity and product depth.",
            "This creates a simple behavioral framework for identifying shallow versus deeper relationships.",
            "The distribution shows where most of the filtered customer population sits in the relationship-strength framework."
        )

    with c2:
        fig_strength_churn = px.line(
            strength_summary,
            x="Relationship Tier",
            y="Churn_Rate",
            markers=True,
            text="Churn_Rate",
            title="Churn Rate Across Relationship Strength"
        )
        fig_strength_churn.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="top center",
            line_width=4,
            marker_size=10
        )
        fig_strength_churn.update_yaxes(ticksuffix="%")
        chart_layout(fig_strength_churn, 430)
        st.plotly_chart(fig_strength_churn, use_container_width=True)

        show_chart_note(
            "The line chart compares churn rates across relationship-strength tiers.",
            "It tests whether stronger combined engagement and product relationships are associated with different churn levels.",
            "The direction of the relationship should be interpreted from the filtered data rather than assuming that every higher score guarantees retention."
        )

    st.subheader("📌 Relationship Strength Score")

    avg_strength = filtered["Relationship Strength"].mean()

    st.progress(
        min(max(avg_strength / 100, 0), 1),
        text=f"Current average relationship strength: {avg_strength:.1f}/100"
    )

    st.write(
        "Scoring logic: Active customer = 50 points; "
        "product depth contributes up to 50 additional points."
    )

with tabs[5]:
    st.header("🚨 High-Value Disengaged Customer Detector")
    st.caption(
        "A practical monitoring view for customers who combine financial value with weak engagement."
    )

    risk = filtered[
        (filtered["Balance"] >= 100000)
        & (filtered["IsActiveMember"] == 0)
    ].copy()

    risk["Risk Signal"] = risk["Exited"].map({
        0: "Inactive / Retained",
        1: "Inactive / Churned"
    })

    risk_display = risk[
        [
            "CustomerId",
            "Geography",
            "Gender",
            "Age",
            "Balance",
            "NumOfProducts",
            "HasCrCard",
            "Exited",
            "Risk Signal"
        ]
    ].sort_values("Balance", ascending=False)

    r1, r2, r3 = st.columns(3)

    with r1:
        st.metric("High-Balance Inactive", f"{len(risk):,}")

    with r2:
        risk_churn = churn_rate(risk)
        st.metric("Risk Segment Churn Rate", pct(risk_churn))

    with r3:
        risk_balance = risk["Balance"].mean() if len(risk) else 0
        st.metric("Avg. Risk-Segment Balance", money(risk_balance))

    st.dataframe(
        risk_display,
        use_container_width=True,
        hide_index=True
    )

    show_chart_note(
        "The table lists customers with balances of at least €100,000 who are inactive.",
        "This is the project's direct detector for potentially valuable but disengaged customers.",
        f"The current filtered view contains {len(risk):,} high-balance inactive customers, with a segment churn rate of {pct(risk_churn)}."
    )

    st.download_button(
        "⬇️ Download Risk Segment CSV",
        data=risk_display.to_csv(index=False).encode("utf-8"),
        file_name="high_value_disengaged_customers.csv",
        mime="text/csv"
    )

with tabs[6]:
    st.header("🔍 Customer Explorer")
    st.caption(
        "Search and inspect individual customer records within the current filter view."
    )

    search_id = st.text_input(
        "Search by Customer ID",
        placeholder="Example: 15634602"
    )

    explorer = filtered.copy()

    if search_id.strip():
        try:
            customer_id = int(search_id.strip())
            explorer = explorer[explorer["CustomerId"] == customer_id]
        except ValueError:
            st.warning("Please enter a numeric Customer ID.")

    display_columns = [
        "CustomerId",
        "Surname",
        "Geography",
        "Gender",
        "Age",
        "CreditScore",
        "Tenure",
        "Balance",
        "NumOfProducts",
        "HasCrCard",
        "IsActiveMember",
        "EstimatedSalary",
        "Exited",
        "Engagement Profile",
        "Relationship Strength"
    ]

    st.dataframe(
        explorer[display_columns].head(500),
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Showing a maximum of 500 rows for browser performance."
    )

st.divider()
st.header("🧠 Automated Retention Insights")
st.caption(
    "These observations are calculated from the currently filtered population."
)

insight_cols = st.columns(3)

highest_profile_row = profile_summary.sort_values(
    "Churn_Rate", ascending=False
).iloc[0]

highest_product_row = product_summary.sort_values(
    "Churn_Rate", ascending=False
).iloc[0]

with insight_cols[0]:
    with st.container(border=True):
        st.subheader("⚡ Engagement Signal")
        st.write(
            f"The highest observed churn rate among the current engagement "
            f"profiles is **{highest_profile_row['Churn_Rate']:.2f}%** "
            f"for **{highest_profile_row['Engagement Profile']}**."
        )
        st.write(
            f"Active retention is **{active_retention:.2f}%**, while "
            f"inactive retention is **{inactive_retention:.2f}%**."
        )

with insight_cols[1]:
    with st.container(border=True):
        st.subheader("📦 Product Signal")
        st.write(
            f"The highest observed churn rate by product count is "
            f"**{highest_product_row['Churn_Rate']:.2f}%** for "
            f"customers with **{int(highest_product_row['NumOfProducts'])} "
            f"product(s)**."
        )
        st.write(
            f"The current Product Depth Index is **{product_depth_index:.1f}**."
        )

with insight_cols[2]:
    with st.container(border=True):
        st.subheader("💰 Financial Signal")
        st.write(
            f"**{len(high_balance_inactive):,}** customers are both "
            f"inactive and have balances of at least **€100,000**."
        )
        st.write(
            f"Their observed churn rate is **{risk_churn:.2f}%**."
        )

st.header("🎯 Retention Strategy Framework")

strategy_cols = st.columns(3)

with strategy_cols[0]:
    with st.container(border=True):
        st.subheader("⚡ Engagement Strategy")
        st.write(
            "Monitor inactive customers and identify segments where "
            "engagement is associated with stronger retention. "
            "Use targeted engagement campaigns for appropriate customer groups."
        )

with strategy_cols[1]:
    with st.container(border=True):
        st.subheader("📦 Product Strategy")
        st.write(
            "Study product-depth patterns before designing bundles. "
            "Use product adoption analysis to identify cross-product "
            "opportunities and relationship-depth patterns."
        )

with strategy_cols[2]:
    with st.container(border=True):
        st.subheader("💎 Premium Customer Protection")
        st.write(
            "Monitor high-balance inactive customers because financial "
            "value and engagement can move in different directions. "
            "Use this group as a retention-monitoring segment."
        )

st.header("🧪 Data Quality & Methodology")

dq1, dq2, dq3, dq4 = st.columns(4)

with dq1:
    st.metric("Rows", f"{len(df):,}")

with dq2:
    st.metric("Columns", f"{len(df.columns):,}")

with dq3:
    st.metric("Missing Values", f"{int(df.isna().sum().sum()):,}")

with dq4:
    st.metric("Duplicate Rows", f"{int(df.duplicated().sum()):,}")

with st.expander("📚 Methodology used in this dashboard"):
    st.write(
        "1. Data ingestion and validation\n\n"
        "2. Engagement classification into behavioral profiles\n\n"
        "3. Product utilization and product-depth analysis\n\n"
        "4. Financial commitment versus engagement analysis\n\n"
        "5. High-value disengaged customer detection\n\n"
        "6. Retention-strength scoring\n\n"
        "7. Interactive filtering and customer-level exploration"
    )

st.markdown("---")
st.subheader("🎯 Customer Risk & Retention Explorer")
st.caption("Explore customer risk levels, individual profiles and product utilization.")

# Create a simple risk score
explorer_df = filtered.copy()

explorer_df["Risk Score"] = (
    (explorer_df["IsActiveMember"] == 0).astype(int) * 40
    + (explorer_df["NumOfProducts"] <= 1).astype(int) * 25
    + (explorer_df["Balance"] >= 100000).astype(int) * 20
    + (explorer_df["Exited"] == 1).astype(int) * 15
)

explorer_df["Risk Level"] = pd.cut(
    explorer_df["Risk Score"],
    bins=[-1, 30, 60, 100],
    labels=["Low Risk", "Medium Risk", "High Risk"]
)

st.markdown("### 🎯 Risk Segmentation")

risk_counts = (
    explorer_df["Risk Level"]
    .value_counts()
    .reindex(["Low Risk", "Medium Risk", "High Risk"])
    .fillna(0)
)

risk_cols = st.columns(3)

for i, risk in enumerate(["Low Risk", "Medium Risk", "High Risk"]):
    with risk_cols[i]:
        with st.container(border=True):
            st.metric(
                risk,
                f"{int(risk_counts[risk]):,}"
            )

st.info(
    "**What this shows:** Customers grouped into low, medium and high-risk segments "
    "using engagement, product depth, balance and churn indicators.\n\n"
    "**Why it matters:** Risk segmentation helps identify customers who may require "
    "stronger retention attention.\n\n"
    "**Key insight:** High-risk customers combine multiple behavioral or financial "
    "signals associated with potential retention risk."
)

st.markdown("### 🔎 Customer Explorer")

customer_ids = explorer_df["CustomerId"].astype(str).tolist()

selected_customer = st.selectbox(
    "Search Customer ID",
    options=["Select a Customer"] + customer_ids
)

if selected_customer != "Select a Customer":

    customer = explorer_df[
        explorer_df["CustomerId"].astype(str) == selected_customer
    ].iloc[0]

    customer_cols = st.columns(4)

    with customer_cols[0]:
        st.metric("Geography", customer["Geography"])

    with customer_cols[1]:
        st.metric("Age", int(customer["Age"]))

    with customer_cols[2]:
        st.metric("Balance", f"€{customer['Balance']:,.0f}")

    with customer_cols[3]:
        st.metric("Products", int(customer["NumOfProducts"]))

    detail_cols = st.columns(4)

    with detail_cols[0]:
        st.metric(
            "Activity",
            "Active" if customer["IsActiveMember"] == 1 else "Inactive"
        )

    with detail_cols[1]:
        st.metric(
            "Credit Card",
            "Yes" if customer["HasCrCard"] == 1 else "No"
        )

    with detail_cols[2]:
        st.metric(
            "Customer Status",
            "Churned" if customer["Exited"] == 1 else "Retained"
        )

    with detail_cols[3]:
        st.metric(
            "Risk Level",
            str(customer["Risk Level"])
        )

st.markdown("### 📦 Product Utilization Explorer")

selected_products = st.selectbox(
    "Select Number of Products",
    options=sorted(explorer_df["NumOfProducts"].unique())
)

product_data = explorer_df[
    explorer_df["NumOfProducts"] == selected_products
]

product_cols = st.columns(4)

product_churn = product_data["Exited"].mean() * 100
product_active = product_data["IsActiveMember"].mean() * 100
product_balance = product_data["Balance"].mean()

with product_cols[0]:
    st.metric(
        "Customers",
        f"{len(product_data):,}"
    )

with product_cols[1]:
    st.metric(
        "Churn Rate",
        f"{product_churn:.1f}%"
    )

with product_cols[2]:
    st.metric(
        "Active Rate",
        f"{product_active:.1f}%"
    )

with product_cols[3]:
    st.metric(
        "Avg Balance",
        f"€{product_balance:,.0f}"
    )

st.info(
    f"**What this shows:** Customer behavior for those using "
    f"{selected_products} product(s).\n\n"
    "**Why it matters:** Product depth can help evaluate relationship strength "
    "and retention behavior.\n\n"
    f"**Key insight:** This segment contains {len(product_data):,} customers "
    f"with a {product_churn:.1f}% churn rate."
)

st.header("📘 Project Information")

info1, info2 = st.columns(2)

with info1:
    with st.container(border=True):
        st.subheader("📌 Project Overview")
        st.write(
            "**Project:** Customer Engagement & Product Utilization Analytics "
            "for Retention Strategy"
        )
        st.write(
            "**Purpose:** Analyze customer behavior, engagement, product depth, "
            "financial commitment and churn patterns to identify retention-focused opportunities."
        )
        st.write("**Internship:** Unified Mentor")
        st.write("**Domain:** Data Analytics")
        st.write("**Developer:** Manya")
        st.write("**Education:** B.Tech – Information Technology")

with info2:
    with st.container(border=True):
        st.subheader("🛠️ Tools & Technologies")
        st.write("**Python** — analytical programming")
        st.write("**Pandas** — data cleaning and transformation")
        st.write("**Streamlit** — interactive dashboard")
        st.write("**Plotly** — interactive visualizations")
        st.write("**VS Code** — development environment")
        st.write("**CSV** — cleaned analytical dataset")

st.markdown("""
<div style="
    margin-top: 100px;
    text-align: center;
    padding: 10px 10px 20px 10px;
">

<p style="
    color: #E9D5FF;
    font-size: 19px;
    font-weight: 600;
    margin: 4px;
">
📊 Customer Engagement & Product Utilization Analytics
</p>

<p style="
    color: #C4B5FD;
    font-size: 14px;
    margin: 6px;
">
Retention Strategy Dashboard
</p>

<p style="
    color: #D8D1E8;
    font-size: 13px;
    margin: 6px;
">
Interactive behavioral analytics for customer retention, product utilization and risk monitoring.
</p>

<p style="
    color: #AAA3C2;
    font-size: 13px;
    margin: 6px;
">
Developed by Manya • B.Tech IT • Unified Mentor Data Analytics Internship
</p>

</div>
""", unsafe_allow_html=True)