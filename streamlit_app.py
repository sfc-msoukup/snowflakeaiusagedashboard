import streamlit as st
import altair as alt
import pandas as pd
from snowflake.snowpark.context import get_active_session

st.set_page_config(
    page_title="Snowflake AI Usage Dashboards",
    page_icon=":snowflake:",
    layout="wide",
)

SNOWFLAKE_BLUE = "#29B5E8"
SNOWFLAKE_DARK = "#11567F"
SNOWFLAKE_LIGHT = "#E8F4FD"
SNOWFLAKE_NAVY = "#1B2A4A"
SNOWFLAKE_BRAND = "#00A1D9"

SNOWFLAKE_PALETTE = ["#29B5E8", "#11567F", "#00A1D9", "#71D4F5", "#0E4D6F", "#A3E4FF", "#086FA3", "#B8ECFF", "#1C8CB8", "#D1F3FF"]

st.markdown(f"""
<style>
    [data-testid="stAppViewContainer"] {{
        background: linear-gradient(180deg, {SNOWFLAKE_LIGHT} 0%, #FFFFFF 30%);
    }}
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {SNOWFLAKE_DARK} 0%, {SNOWFLAKE_NAVY} 100%);
    }}
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
        color: #FFFFFF !important;
    }}
    [data-testid="stSidebar"] .stSelectbox label {{
        color: #A3E4FF !important;
    }}
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"],
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] * {{
        color: {SNOWFLAKE_NAVY} !important;
    }}
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] svg {{
        fill: {SNOWFLAKE_NAVY} !important;
    }}
    [data-testid="stSidebar"] [role="option"] {{
        color: {SNOWFLAKE_NAVY} !important;
    }}
    [data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,0.2) !important;
    }}
    h1 {{
        color: {SNOWFLAKE_NAVY} !important;
    }}
    h2, h3, [data-testid="stHeader"] {{
        color: {SNOWFLAKE_DARK} !important;
    }}
    [data-testid="stMetricValue"] {{
        color: {SNOWFLAKE_BRAND} !important;
        font-weight: 700 !important;
    }}
    [data-testid="stMetricLabel"] {{
        color: {SNOWFLAKE_NAVY} !important;
        font-weight: 600 !important;
    }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: 2px;
        background-color: {SNOWFLAKE_LIGHT};
        border-radius: 8px;
        padding: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 6px;
        color: {SNOWFLAKE_DARK};
        font-weight: 500;
        background-color: #B8ECFF !important;
        padding-left: 5px !important;
        padding-right: 5px !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {SNOWFLAKE_BLUE} !important;
        color: white !important;
    }}
    .stDataFrame {{
        border: 1px solid {SNOWFLAKE_LIGHT} !important;
        border-radius: 8px;
    }}
</style>
""", unsafe_allow_html=True)

session = get_active_session()


@st.cache_data(ttl=600)
def run_query(sql: str) -> pd.DataFrame:
    return session.sql(sql).to_pandas()


def safe_query(sql: str) -> pd.DataFrame:
    try:
        df = run_query(sql)
        if df is not None and not df.empty:
            return df
    except Exception:
        pass
    return pd.DataFrame()


def format_credits(val) -> str:
    if pd.isna(val) or val is None:
        return "0.00"
    if val >= 1000:
        return f"{val:,.0f}"
    if val >= 1:
        return f"{val:,.2f}"
    return f"{val:,.4f}"


def render_daily_chart(df: pd.DataFrame, date_col: str, credit_col: str, color_col: str = None):
    if df.empty:
        return
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    if color_col and color_col in df.columns:
        chart = alt.Chart(df).mark_area(opacity=0.7, line=True).encode(
            x=alt.X(f"{date_col}:T", title="Date"),
            y=alt.Y(f"{credit_col}:Q", title="Credits", stack=True),
            color=alt.Color(f"{color_col}:N", title=color_col.replace("_", " ").title(),
                            scale=alt.Scale(range=SNOWFLAKE_PALETTE)),
            tooltip=[
                alt.Tooltip(f"{date_col}:T", title="Date"),
                alt.Tooltip(f"{color_col}:N", title=color_col.replace("_", " ").title()),
                alt.Tooltip(f"{credit_col}:Q", title="Credits", format=",.4f"),
            ],
        )
    else:
        chart = alt.Chart(df).mark_area(
            opacity=0.7, line=True,
            color=alt.Gradient(gradient="linear", stops=[
                alt.GradientStop(color=SNOWFLAKE_BLUE, offset=0),
                alt.GradientStop(color=SNOWFLAKE_LIGHT, offset=1),
            ], x1=0, x2=0, y1=0, y2=1)
        ).encode(
            x=alt.X(f"{date_col}:T", title="Date"),
            y=alt.Y(f"{credit_col}:Q", title="Credits"),
            tooltip=[
                alt.Tooltip(f"{date_col}:T", title="Date"),
                alt.Tooltip(f"{credit_col}:Q", title="Credits", format=",.4f"),
            ],
        )
    st.altair_chart(chart, use_container_width=True)


with st.sidebar:
    st.title(":snowflake: AI Usage Dashboards")
    st.markdown("---")
    date_range = st.selectbox(
        "Time Period",
        ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last 180 Days", "Last Year", "Custom"],
        index=1,
    )
    days_map = {
        "Last 7 Days": 7,
        "Last 30 Days": 30,
        "Last 90 Days": 90,
        "Last 180 Days": 180,
        "Last Year": 365,
    }
    if date_range == "Custom":
        from datetime import date, timedelta
        default_start = date.today() - timedelta(days=30)
        custom_start = st.date_input("From", value=default_start)
        custom_end = st.date_input("To", value=date.today())
        date_filter = f"'{custom_start.strftime('%Y-%m-%d')}'"
        date_filter_end = f"'{custom_end.strftime('%Y-%m-%d')}'"
    else:
        days = days_map[date_range]
        date_filter = f"DATEADD(DAY, -{days}, CURRENT_DATE())"
        date_filter_end = "CURRENT_DATE()"

    st.markdown("---")
    st.caption("Data from SNOWFLAKE.ACCOUNT_USAGE")
    st.caption("Requires ACCOUNTADMIN or GOVERNANCE_VIEWER role.")

st.title(":snowflake: Snowflake AI Usage Dashboards")

overview_sql = f"""
SELECT 'Cortex LLM Functions' AS SERVICE, ROUND(SUM(TOKEN_CREDITS), 4) AS CREDITS
FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_FUNCTIONS_USAGE_HISTORY
WHERE START_TIME >= {date_filter} AND START_TIME <= {date_filter_end}
UNION ALL
SELECT 'AI SQL Functions', ROUND(SUM(TOKEN_CREDITS), 4)
FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AISQL_USAGE_HISTORY
WHERE USAGE_TIME >= {date_filter} AND USAGE_TIME <= {date_filter_end}
UNION ALL
SELECT 'Cortex Analyst', ROUND(SUM(CREDITS), 4)
FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_ANALYST_USAGE_HISTORY
WHERE START_TIME >= {date_filter} AND START_TIME <= {date_filter_end}
UNION ALL
SELECT 'Cortex Search', ROUND(SUM(CREDITS), 4)
FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_SEARCH_DAILY_USAGE_HISTORY
WHERE USAGE_DATE >= {date_filter} AND USAGE_DATE <= {date_filter_end}
UNION ALL
SELECT 'Cortex Search (Serving)', ROUND(SUM(CREDITS), 4)
FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_SEARCH_SERVING_USAGE_HISTORY
WHERE START_TIME >= {date_filter} AND START_TIME <= {date_filter_end}
UNION ALL
SELECT 'Cortex Code', ROUND(SUM(TOKEN_CREDITS), 4)
FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_CODE_CLI_USAGE_HISTORY
WHERE USAGE_TIME >= {date_filter} AND USAGE_TIME <= {date_filter_end}
UNION ALL
SELECT 'Cortex Agent', ROUND(SUM(TOKEN_CREDITS), 4)
FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AGENT_USAGE_HISTORY
WHERE START_TIME >= {date_filter} AND START_TIME <= {date_filter_end}
UNION ALL
SELECT 'Snowflake Intelligence', ROUND(SUM(TOKEN_CREDITS), 4)
FROM SNOWFLAKE.ACCOUNT_USAGE.SNOWFLAKE_INTELLIGENCE_USAGE_HISTORY
WHERE START_TIME >= {date_filter} AND START_TIME <= {date_filter_end}
UNION ALL
SELECT 'Document AI', ROUND(SUM(CREDITS_USED), 4)
FROM SNOWFLAKE.ACCOUNT_USAGE.DOCUMENT_AI_USAGE_HISTORY
WHERE START_TIME >= {date_filter} AND START_TIME <= {date_filter_end}
"""

tabs = st.tabs([
    "Overview",
    "Cortex LLM Functions",
    "AI SQL Functions",
    "Cortex Analyst",
    "Cortex Search",
    "Cortex Code",
    "Cortex Agent",
    "Snowflake Intelligence",
    "Document AI",
])

# ============================
# TAB: Overview
# ============================
with tabs[0]:
    df_overview = safe_query(overview_sql)
    if not df_overview.empty:
        df_overview = df_overview.fillna(0)
        total_credits = df_overview["CREDITS"].sum()

        k1, k2 = st.columns(2)
        k1.metric("Total AI Credits", format_credits(total_credits))
        active_services = len(df_overview[df_overview["CREDITS"] > 0])
        k2.metric("Active Services", str(active_services))

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Credits by Service")
            df_chart = df_overview[df_overview["CREDITS"] > 0].sort_values("CREDITS", ascending=True)
            if not df_chart.empty:
                chart = alt.Chart(df_chart).mark_bar(cornerRadiusEnd=4).encode(
                    x=alt.X("CREDITS:Q", title="Credits"),
                    y=alt.Y("SERVICE:N", title="", sort="-x"),
                    color=alt.Color("SERVICE:N", legend=None, scale=alt.Scale(range=SNOWFLAKE_PALETTE)),
                    tooltip=[
                        alt.Tooltip("SERVICE:N", title="Service"),
                        alt.Tooltip("CREDITS:Q", title="Credits", format=",.4f"),
                    ],
                )
                st.altair_chart(chart, use_container_width=True)

        with col2:
            st.subheader("Credit Distribution")
            df_pie = df_overview[df_overview["CREDITS"] > 0].copy()
            if not df_pie.empty:
                chart = alt.Chart(df_pie).mark_arc(innerRadius=50).encode(
                    theta=alt.Theta("CREDITS:Q"),
                    color=alt.Color("SERVICE:N", title="Service", scale=alt.Scale(range=SNOWFLAKE_PALETTE)),
                    tooltip=[
                        alt.Tooltip("SERVICE:N", title="Service"),
                        alt.Tooltip("CREDITS:Q", title="Credits", format=",.4f"),
                    ],
                )
                st.altair_chart(chart, use_container_width=True)

        daily_trend_sql = f"""
        SELECT DATE(START_TIME) AS USAGE_DATE, 'Cortex LLM Functions' AS SERVICE, ROUND(SUM(TOKEN_CREDITS), 4) AS CREDITS
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_FUNCTIONS_USAGE_HISTORY
        WHERE START_TIME >= {date_filter} AND START_TIME <= {date_filter_end} GROUP BY 1
        UNION ALL
        SELECT DATE(USAGE_TIME), 'AI SQL Functions', ROUND(SUM(TOKEN_CREDITS), 4)
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AISQL_USAGE_HISTORY
        WHERE USAGE_TIME >= {date_filter} AND USAGE_TIME <= {date_filter_end} GROUP BY 1
        UNION ALL
        SELECT DATE(START_TIME), 'Cortex Analyst', ROUND(SUM(CREDITS), 4)
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_ANALYST_USAGE_HISTORY
        WHERE START_TIME >= {date_filter} AND START_TIME <= {date_filter_end} GROUP BY 1
        UNION ALL
        SELECT USAGE_DATE, 'Cortex Search', ROUND(SUM(CREDITS), 4)
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_SEARCH_DAILY_USAGE_HISTORY
        WHERE USAGE_DATE >= {date_filter} AND USAGE_DATE <= {date_filter_end} GROUP BY 1
        UNION ALL
        SELECT DATE(USAGE_TIME), 'Cortex Code', ROUND(SUM(TOKEN_CREDITS), 4)
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_CODE_CLI_USAGE_HISTORY
        WHERE USAGE_TIME >= {date_filter} AND USAGE_TIME <= {date_filter_end} GROUP BY 1
        UNION ALL
        SELECT DATE(START_TIME), 'Cortex Agent', ROUND(SUM(TOKEN_CREDITS), 4)
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AGENT_USAGE_HISTORY
        WHERE START_TIME >= {date_filter} AND START_TIME <= {date_filter_end} GROUP BY 1
        UNION ALL
        SELECT DATE(START_TIME), 'Snowflake Intelligence', ROUND(SUM(TOKEN_CREDITS), 4)
        FROM SNOWFLAKE.ACCOUNT_USAGE.SNOWFLAKE_INTELLIGENCE_USAGE_HISTORY
        WHERE START_TIME >= {date_filter} AND START_TIME <= {date_filter_end} GROUP BY 1
        UNION ALL
        SELECT DATE(START_TIME), 'Document AI', ROUND(SUM(CREDITS_USED), 4)
        FROM SNOWFLAKE.ACCOUNT_USAGE.DOCUMENT_AI_USAGE_HISTORY
        WHERE START_TIME >= {date_filter} AND START_TIME <= {date_filter_end} GROUP BY 1
        ORDER BY USAGE_DATE
        """
        st.subheader("Daily AI Credit Usage (All Services)")
        df_daily = safe_query(daily_trend_sql)
        if not df_daily.empty:
            render_daily_chart(df_daily, "USAGE_DATE", "CREDITS", "SERVICE")

        st.subheader("Service Breakdown Table")
        df_table = df_overview.sort_values("CREDITS", ascending=False).rename(columns={"SERVICE": "Service", "CREDITS": "Credits"}).reset_index(drop=True)
        st.dataframe(df_table)
    else:
        st.warning("No AI usage data found for the selected period.")

# ============================
# TAB: Cortex LLM Functions
# ============================
with tabs[1]:
    st.header("Cortex LLM Functions")
    st.caption("Usage of COMPLETE, TRANSLATE, SUMMARIZE, EXTRACT_ANSWER, SENTIMENT, and other Cortex LLM functions.")

    llm_summary_sql = f"""
    SELECT
        FUNCTION_NAME,
        MODEL_NAME,
        ROUND(SUM(TOKEN_CREDITS), 4) AS CREDITS,
        SUM(TOKENS) AS TOTAL_TOKENS,
        COUNT(*) AS USAGE_HOURS
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_FUNCTIONS_USAGE_HISTORY
    WHERE START_TIME >= {date_filter} AND START_TIME <= {date_filter_end}
    GROUP BY FUNCTION_NAME, MODEL_NAME
    ORDER BY CREDITS DESC
    """
    df_llm = safe_query(llm_summary_sql)
    if not df_llm.empty:
        total_creds = df_llm["CREDITS"].sum()
        total_tokens = df_llm["TOTAL_TOKENS"].sum()
        k1, k2, k3 = st.columns(3)
        k1.metric("Total Credits", format_credits(total_creds))
        k2.metric("Total Tokens", f"{total_tokens:,.0f}")
        k3.metric("Models Used", str(df_llm["MODEL_NAME"].nunique()))

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Credits by Model")
            df_model = df_llm.groupby("MODEL_NAME", as_index=False)["CREDITS"].sum().sort_values("CREDITS", ascending=True)
            chart = alt.Chart(df_model).mark_bar(cornerRadiusEnd=4).encode(
                x=alt.X("CREDITS:Q", title="Credits"),
                y=alt.Y("MODEL_NAME:N", title="", sort="-x"),
                color=alt.Color("MODEL_NAME:N", legend=None, scale=alt.Scale(range=SNOWFLAKE_PALETTE)),
                tooltip=[alt.Tooltip("MODEL_NAME:N"), alt.Tooltip("CREDITS:Q", format=",.4f")],
            )
            st.altair_chart(chart, use_container_width=True)

        with col2:
            st.subheader("Credits by Function")
            df_func = df_llm.groupby("FUNCTION_NAME", as_index=False)["CREDITS"].sum().sort_values("CREDITS", ascending=True)
            chart = alt.Chart(df_func).mark_bar(cornerRadiusEnd=4).encode(
                x=alt.X("CREDITS:Q", title="Credits"),
                y=alt.Y("FUNCTION_NAME:N", title="", sort="-x"),
                color=alt.Color("FUNCTION_NAME:N", legend=None, scale=alt.Scale(range=SNOWFLAKE_PALETTE)),
                tooltip=[alt.Tooltip("FUNCTION_NAME:N"), alt.Tooltip("CREDITS:Q", format=",.4f")],
            )
            st.altair_chart(chart, use_container_width=True)

        llm_daily_sql = f"""
        SELECT DATE(START_TIME) AS USAGE_DATE, MODEL_NAME, ROUND(SUM(TOKEN_CREDITS), 4) AS CREDITS
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_FUNCTIONS_USAGE_HISTORY
        WHERE START_TIME >= {date_filter} AND START_TIME <= {date_filter_end}
        GROUP BY 1, 2 ORDER BY 1
        """
        st.subheader("Daily Trend by Model")
        df_llm_daily = safe_query(llm_daily_sql)
        if not df_llm_daily.empty:
            render_daily_chart(df_llm_daily, "USAGE_DATE", "CREDITS", "MODEL_NAME")

        st.subheader("Detailed Breakdown")
        df_table = df_llm.rename(columns={"FUNCTION_NAME": "Function", "MODEL_NAME": "Model", "CREDITS": "Credits", "TOTAL_TOKENS": "Tokens", "USAGE_HOURS": "Usage Hours"}).reset_index(drop=True)
        st.dataframe(df_table)
    else:
        st.info("No Cortex LLM Function usage found for the selected period.")

# ============================
# TAB: AI SQL Functions
# ============================
with tabs[2]:
    st.header("AI SQL Functions")
    st.caption("Usage of AI_COMPLETE, AI_EMBED, AI_CLASSIFY, AI_SUMMARIZE and other AI SQL functions.")

    aisql_sql = f"""
    SELECT
        FUNCTION_NAME,
        MODEL_NAME,
        ROUND(SUM(TOKEN_CREDITS), 4) AS CREDITS,
        SUM(TOKENS) AS TOTAL_TOKENS,
        COUNT(DISTINCT QUERY_ID) AS QUERY_COUNT
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AISQL_USAGE_HISTORY
    WHERE USAGE_TIME >= {date_filter} AND USAGE_TIME <= {date_filter_end}
    GROUP BY FUNCTION_NAME, MODEL_NAME
    ORDER BY CREDITS DESC
    """
    df_aisql = safe_query(aisql_sql)
    if not df_aisql.empty:
        total_creds = df_aisql["CREDITS"].sum()
        total_tokens = df_aisql["TOTAL_TOKENS"].sum()
        k1, k2, k3 = st.columns(3)
        k1.metric("Total Credits", format_credits(total_creds))
        k2.metric("Total Tokens", f"{total_tokens:,.0f}")
        k3.metric("Distinct Queries", f"{df_aisql['QUERY_COUNT'].sum():,.0f}")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Credits by Function")
            df_func = df_aisql.groupby("FUNCTION_NAME", as_index=False)["CREDITS"].sum().sort_values("CREDITS", ascending=True)
            chart = alt.Chart(df_func).mark_bar(cornerRadiusEnd=4).encode(
                x=alt.X("CREDITS:Q", title="Credits"),
                y=alt.Y("FUNCTION_NAME:N", title="", sort="-x"),
                color=alt.Color("FUNCTION_NAME:N", legend=None, scale=alt.Scale(range=SNOWFLAKE_PALETTE)),
                tooltip=[alt.Tooltip("FUNCTION_NAME:N"), alt.Tooltip("CREDITS:Q", format=",.4f")],
            )
            st.altair_chart(chart, use_container_width=True)

        with col2:
            st.subheader("Credits by Model")
            df_model = df_aisql.groupby("MODEL_NAME", as_index=False)["CREDITS"].sum().sort_values("CREDITS", ascending=True)
            chart = alt.Chart(df_model).mark_bar(cornerRadiusEnd=4).encode(
                x=alt.X("CREDITS:Q", title="Credits"),
                y=alt.Y("MODEL_NAME:N", title="", sort="-x"),
                color=alt.Color("MODEL_NAME:N", legend=None, scale=alt.Scale(range=SNOWFLAKE_PALETTE)),
                tooltip=[alt.Tooltip("MODEL_NAME:N"), alt.Tooltip("CREDITS:Q", format=",.4f")],
            )
            st.altair_chart(chart, use_container_width=True)

        aisql_daily_sql = f"""
        SELECT DATE(USAGE_TIME) AS USAGE_DATE, FUNCTION_NAME, ROUND(SUM(TOKEN_CREDITS), 4) AS CREDITS
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AISQL_USAGE_HISTORY
        WHERE USAGE_TIME >= {date_filter} AND USAGE_TIME <= {date_filter_end}
        GROUP BY 1, 2 ORDER BY 1
        """
        st.subheader("Daily Trend")
        df_aisql_daily = safe_query(aisql_daily_sql)
        if not df_aisql_daily.empty:
            render_daily_chart(df_aisql_daily, "USAGE_DATE", "CREDITS", "FUNCTION_NAME")

        st.subheader("Detailed Breakdown")
        st.dataframe(df_aisql.reset_index(drop=True))
    else:
        st.info("No AI SQL Function usage found for the selected period.")

# ============================
# TAB: Cortex Analyst
# ============================
with tabs[3]:
    st.header("Cortex Analyst")
    st.caption("Natural language to SQL service usage.")

    analyst_sql = f"""
    SELECT
        USERNAME,
        ROUND(SUM(CREDITS), 4) AS CREDITS,
        SUM(REQUEST_COUNT) AS REQUESTS,
        ROUND(SUM(CREDITS) / NULLIF(SUM(REQUEST_COUNT), 0), 6) AS AVG_CREDIT_PER_REQUEST,
        COUNT(DISTINCT DATE(START_TIME)) AS ACTIVE_DAYS
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_ANALYST_USAGE_HISTORY
    WHERE START_TIME >= {date_filter} AND START_TIME <= {date_filter_end}
    GROUP BY USERNAME
    ORDER BY CREDITS DESC
    """
    df_analyst = safe_query(analyst_sql)
    if not df_analyst.empty:
        total_creds = df_analyst["CREDITS"].sum()
        total_reqs = df_analyst["REQUESTS"].sum()
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Credits", format_credits(total_creds))
        k2.metric("Total Requests", f"{total_reqs:,.0f}")
        k3.metric("Active Users", str(len(df_analyst)))
        avg_per_req = total_creds / total_reqs if total_reqs > 0 else 0
        k4.metric("Avg Credit/Request", format_credits(avg_per_req))

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Credits by User")
            chart = alt.Chart(df_analyst).mark_bar(cornerRadiusEnd=4).encode(
                x=alt.X("CREDITS:Q", title="Credits"),
                y=alt.Y("USERNAME:N", title="", sort="-x"),
                color=alt.Color("USERNAME:N", legend=None, scale=alt.Scale(range=SNOWFLAKE_PALETTE)),
                tooltip=[alt.Tooltip("USERNAME:N"), alt.Tooltip("CREDITS:Q", format=",.4f"), alt.Tooltip("REQUESTS:Q", title="Requests")],
            )
            st.altair_chart(chart, use_container_width=True)

        with col2:
            analyst_daily_sql = f"""
            SELECT DATE(START_TIME) AS USAGE_DATE, ROUND(SUM(CREDITS), 4) AS CREDITS, SUM(REQUEST_COUNT) AS REQUESTS
            FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_ANALYST_USAGE_HISTORY
            WHERE START_TIME >= {date_filter} AND START_TIME <= {date_filter_end}
            GROUP BY 1 ORDER BY 1
            """
            st.subheader("Daily Trend")
            df_analyst_daily = safe_query(analyst_daily_sql)
            if not df_analyst_daily.empty:
                render_daily_chart(df_analyst_daily, "USAGE_DATE", "CREDITS")

        st.subheader("User Breakdown")
        df_table = df_analyst.rename(columns={"USERNAME": "User", "CREDITS": "Credits", "REQUESTS": "Requests", "AVG_CREDIT_PER_REQUEST": "Avg Credit/Req", "ACTIVE_DAYS": "Active Days"}).reset_index(drop=True)
        st.dataframe(df_table)
    else:
        st.info("No Cortex Analyst usage found for the selected period.")

# ============================
# TAB: Cortex Search
# ============================
with tabs[4]:
    st.header("Cortex Search")
    st.caption("Search service usage including indexing and serving costs.")

    search_sql = f"""
    SELECT
        SERVICE_NAME,
        DATABASE_NAME,
        SCHEMA_NAME,
        CONSUMPTION_TYPE,
        ROUND(SUM(CREDITS), 4) AS CREDITS
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_SEARCH_DAILY_USAGE_HISTORY
    WHERE USAGE_DATE >= {date_filter} AND USAGE_DATE <= {date_filter_end}
    GROUP BY SERVICE_NAME, DATABASE_NAME, SCHEMA_NAME, CONSUMPTION_TYPE
    ORDER BY CREDITS DESC
    """
    df_search = safe_query(search_sql)

    serving_sql = f"""
    SELECT
        SERVICE_NAME,
        DATABASE_NAME,
        SCHEMA_NAME,
        ROUND(SUM(CREDITS), 4) AS CREDITS
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_SEARCH_SERVING_USAGE_HISTORY
    WHERE START_TIME >= {date_filter} AND START_TIME <= {date_filter_end}
    GROUP BY SERVICE_NAME, DATABASE_NAME, SCHEMA_NAME
    ORDER BY CREDITS DESC
    """
    df_serving = safe_query(serving_sql)

    total_search = (df_search["CREDITS"].sum() if not df_search.empty else 0) + (df_serving["CREDITS"].sum() if not df_serving.empty else 0)
    services_count = (df_search["SERVICE_NAME"].nunique() if not df_search.empty else 0)

    if total_search > 0:
        k1, k2 = st.columns(2)
        k1.metric("Total Search Credits", format_credits(total_search))
        k2.metric("Search Services", str(services_count))

        if not df_search.empty:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Credits by Service")
                df_svc = df_search.groupby("SERVICE_NAME", as_index=False)["CREDITS"].sum().sort_values("CREDITS", ascending=True)
                chart = alt.Chart(df_svc).mark_bar(cornerRadiusEnd=4).encode(
                    x=alt.X("CREDITS:Q", title="Credits"),
                    y=alt.Y("SERVICE_NAME:N", title="", sort="-x"),
                    color=alt.Color("SERVICE_NAME:N", legend=None, scale=alt.Scale(range=SNOWFLAKE_PALETTE)),
                    tooltip=[alt.Tooltip("SERVICE_NAME:N"), alt.Tooltip("CREDITS:Q", format=",.4f")],
                )
                st.altair_chart(chart, use_container_width=True)

            with col2:
                st.subheader("Credits by Consumption Type")
                df_type = df_search.groupby("CONSUMPTION_TYPE", as_index=False)["CREDITS"].sum()
                chart = alt.Chart(df_type).mark_arc(innerRadius=50).encode(
                    theta=alt.Theta("CREDITS:Q"),
                    color=alt.Color("CONSUMPTION_TYPE:N", scale=alt.Scale(range=SNOWFLAKE_PALETTE)),
                    tooltip=[alt.Tooltip("CONSUMPTION_TYPE:N"), alt.Tooltip("CREDITS:Q", format=",.4f")],
                )
                st.altair_chart(chart, use_container_width=True)

            search_daily_sql = f"""
            SELECT USAGE_DATE, SERVICE_NAME, ROUND(SUM(CREDITS), 4) AS CREDITS
            FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_SEARCH_DAILY_USAGE_HISTORY
            WHERE USAGE_DATE >= {date_filter} AND USAGE_DATE <= {date_filter_end}
            GROUP BY 1, 2 ORDER BY 1
            """
            st.subheader("Daily Search Trend")
            df_search_daily = safe_query(search_daily_sql)
            if not df_search_daily.empty:
                render_daily_chart(df_search_daily, "USAGE_DATE", "CREDITS", "SERVICE_NAME")

        st.subheader("Search Service Details")
        st.dataframe((df_search if not df_search.empty else df_serving).reset_index(drop=True))
    else:
        st.info("No Cortex Search usage found for the selected period.")

# ============================
# TAB: Cortex Code
# ============================
with tabs[5]:
    st.header("Cortex Code")
    st.caption("Cortex Code CLI (AI-powered coding assistant) usage.")

    code_sql = f"""
    SELECT
        USER_ID,
        ROUND(SUM(TOKEN_CREDITS), 4) AS CREDITS,
        SUM(TOKENS) AS TOTAL_TOKENS,
        COUNT(DISTINCT REQUEST_ID) AS REQUESTS
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_CODE_CLI_USAGE_HISTORY
    WHERE USAGE_TIME >= {date_filter} AND USAGE_TIME <= {date_filter_end}
    GROUP BY USER_ID
    ORDER BY CREDITS DESC
    """
    df_code = safe_query(code_sql)
    if not df_code.empty:
        total_creds = df_code["CREDITS"].sum()
        total_tokens = df_code["TOTAL_TOKENS"].sum()
        total_reqs = df_code["REQUESTS"].sum()
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Credits", format_credits(total_creds))
        k2.metric("Total Tokens", f"{total_tokens:,.0f}")
        k3.metric("Total Requests", f"{total_reqs:,.0f}")
        k4.metric("Active Users", str(len(df_code)))

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Credits by User")
            df_code["USER_ID"] = df_code["USER_ID"].astype(str)
            chart = alt.Chart(df_code).mark_bar(cornerRadiusEnd=4).encode(
                x=alt.X("CREDITS:Q", title="Credits"),
                y=alt.Y("USER_ID:N", title="User ID", sort="-x"),
                color=alt.Color("USER_ID:N", legend=None, scale=alt.Scale(range=SNOWFLAKE_PALETTE)),
                tooltip=[alt.Tooltip("USER_ID:N"), alt.Tooltip("CREDITS:Q", format=",.4f"), alt.Tooltip("TOTAL_TOKENS:Q", title="Tokens")],
            )
            st.altair_chart(chart, use_container_width=True)

        with col2:
            code_daily_sql = f"""
            SELECT DATE(USAGE_TIME) AS USAGE_DATE, ROUND(SUM(TOKEN_CREDITS), 4) AS CREDITS, SUM(TOKENS) AS TOTAL_TOKENS
            FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_CODE_CLI_USAGE_HISTORY
            WHERE USAGE_TIME >= {date_filter} AND USAGE_TIME <= {date_filter_end}
            GROUP BY 1 ORDER BY 1
            """
            st.subheader("Daily Trend")
            df_code_daily = safe_query(code_daily_sql)
            if not df_code_daily.empty:
                render_daily_chart(df_code_daily, "USAGE_DATE", "CREDITS")

        st.subheader("User Breakdown")
        st.dataframe(df_code.reset_index(drop=True))
    else:
        st.info("No Cortex Code usage found for the selected period.")

# ============================
# TAB: Cortex Agent
# ============================
with tabs[6]:
    st.header("Cortex Agent")
    st.caption("Cortex Agent API usage for building agentic applications.")

    agent_sql = f"""
    SELECT
        COALESCE(USER_NAME, CAST(USER_ID AS VARCHAR)) AS USER_DISPLAY,
        COALESCE(AGENT_NAME, 'N/A') AS AGENT_NAME,
        COALESCE(AGENT_DATABASE_NAME, '') AS DATABASE_NAME,
        COALESCE(AGENT_SCHEMA_NAME, '') AS SCHEMA_NAME,
        ROUND(SUM(TOKEN_CREDITS), 4) AS CREDITS,
        SUM(TOKENS) AS TOTAL_TOKENS,
        COUNT(DISTINCT REQUEST_ID) AS REQUESTS
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AGENT_USAGE_HISTORY
    WHERE START_TIME >= {date_filter} AND START_TIME <= {date_filter_end}
    GROUP BY 1, 2, 3, 4
    ORDER BY CREDITS DESC
    """
    df_agent = safe_query(agent_sql)
    if not df_agent.empty:
        total_creds = df_agent["CREDITS"].sum()
        total_reqs = df_agent["REQUESTS"].sum()
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Credits", format_credits(total_creds))
        k2.metric("Total Requests", f"{total_reqs:,.0f}")
        k3.metric("Active Users", str(df_agent["USER_DISPLAY"].nunique()))
        k4.metric("Agents Used", str(df_agent[df_agent["AGENT_NAME"] != "N/A"]["AGENT_NAME"].nunique()))

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Credits by User")
            df_user = df_agent.groupby("USER_DISPLAY", as_index=False)["CREDITS"].sum().sort_values("CREDITS", ascending=True)
            chart = alt.Chart(df_user).mark_bar(cornerRadiusEnd=4).encode(
                x=alt.X("CREDITS:Q", title="Credits"),
                y=alt.Y("USER_DISPLAY:N", title="", sort="-x"),
                color=alt.Color("USER_DISPLAY:N", legend=None, scale=alt.Scale(range=SNOWFLAKE_PALETTE)),
                tooltip=[alt.Tooltip("USER_DISPLAY:N", title="User"), alt.Tooltip("CREDITS:Q", format=",.4f")],
            )
            st.altair_chart(chart, use_container_width=True)

        with col2:
            st.subheader("Credits by Agent")
            df_ag = df_agent.groupby("AGENT_NAME", as_index=False)["CREDITS"].sum().sort_values("CREDITS", ascending=True)
            chart = alt.Chart(df_ag).mark_bar(cornerRadiusEnd=4).encode(
                x=alt.X("CREDITS:Q", title="Credits"),
                y=alt.Y("AGENT_NAME:N", title="", sort="-x"),
                color=alt.Color("AGENT_NAME:N", legend=None, scale=alt.Scale(range=SNOWFLAKE_PALETTE)),
                tooltip=[alt.Tooltip("AGENT_NAME:N"), alt.Tooltip("CREDITS:Q", format=",.4f")],
            )
            st.altair_chart(chart, use_container_width=True)

        agent_daily_sql = f"""
        SELECT DATE(START_TIME) AS USAGE_DATE, COALESCE(USER_NAME, CAST(USER_ID AS VARCHAR)) AS USER_DISPLAY,
            ROUND(SUM(TOKEN_CREDITS), 4) AS CREDITS
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AGENT_USAGE_HISTORY
        WHERE START_TIME >= {date_filter} AND START_TIME <= {date_filter_end}
        GROUP BY 1, 2 ORDER BY 1
        """
        st.subheader("Daily Trend")
        df_agent_daily = safe_query(agent_daily_sql)
        if not df_agent_daily.empty:
            render_daily_chart(df_agent_daily, "USAGE_DATE", "CREDITS", "USER_DISPLAY")

        st.subheader("Agent Details")
        st.dataframe(df_agent.reset_index(drop=True))
    else:
        st.info("No Cortex Agent usage found for the selected period.")

# ============================
# TAB: Snowflake Intelligence
# ============================
with tabs[7]:
    st.header("Snowflake Intelligence")
    st.caption("Snowflake Intelligence (AI-powered analytics assistant) usage.")

    intel_sql = f"""
    SELECT
        COALESCE(USER_NAME, CAST(USER_ID AS VARCHAR)) AS USER_DISPLAY,
        COALESCE(SNOWFLAKE_INTELLIGENCE_NAME, 'N/A') AS INTELLIGENCE_NAME,
        COALESCE(AGENT_NAME, '') AS AGENT_NAME,
        COALESCE(AGENT_DATABASE_NAME, '') AS DATABASE_NAME,
        ROUND(SUM(TOKEN_CREDITS), 4) AS CREDITS,
        SUM(TOKENS) AS TOTAL_TOKENS,
        COUNT(DISTINCT REQUEST_ID) AS REQUESTS
    FROM SNOWFLAKE.ACCOUNT_USAGE.SNOWFLAKE_INTELLIGENCE_USAGE_HISTORY
    WHERE START_TIME >= {date_filter} AND START_TIME <= {date_filter_end}
    GROUP BY 1, 2, 3, 4
    ORDER BY CREDITS DESC
    """
    df_intel = safe_query(intel_sql)
    if not df_intel.empty:
        total_creds = df_intel["CREDITS"].sum()
        total_reqs = df_intel["REQUESTS"].sum()
        k1, k2, k3 = st.columns(3)
        k1.metric("Total Credits", format_credits(total_creds))
        k2.metric("Total Requests", f"{total_reqs:,.0f}")
        k3.metric("Active Users", str(df_intel["USER_DISPLAY"].nunique()))

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Credits by User")
            df_user = df_intel.groupby("USER_DISPLAY", as_index=False)["CREDITS"].sum().sort_values("CREDITS", ascending=True)
            chart = alt.Chart(df_user).mark_bar(cornerRadiusEnd=4).encode(
                x=alt.X("CREDITS:Q", title="Credits"),
                y=alt.Y("USER_DISPLAY:N", title="", sort="-x"),
                color=alt.Color("USER_DISPLAY:N", legend=None, scale=alt.Scale(range=SNOWFLAKE_PALETTE)),
                tooltip=[alt.Tooltip("USER_DISPLAY:N", title="User"), alt.Tooltip("CREDITS:Q", format=",.4f")],
            )
            st.altair_chart(chart, use_container_width=True)

        with col2:
            st.subheader("Credits by Intelligence App")
            df_app = df_intel.groupby("INTELLIGENCE_NAME", as_index=False)["CREDITS"].sum().sort_values("CREDITS", ascending=True)
            chart = alt.Chart(df_app).mark_bar(cornerRadiusEnd=4).encode(
                x=alt.X("CREDITS:Q", title="Credits"),
                y=alt.Y("INTELLIGENCE_NAME:N", title="", sort="-x"),
                color=alt.Color("INTELLIGENCE_NAME:N", legend=None, scale=alt.Scale(range=SNOWFLAKE_PALETTE)),
                tooltip=[alt.Tooltip("INTELLIGENCE_NAME:N"), alt.Tooltip("CREDITS:Q", format=",.4f")],
            )
            st.altair_chart(chart, use_container_width=True)

        intel_daily_sql = f"""
        SELECT DATE(START_TIME) AS USAGE_DATE, ROUND(SUM(TOKEN_CREDITS), 4) AS CREDITS, SUM(TOKENS) AS TOTAL_TOKENS
        FROM SNOWFLAKE.ACCOUNT_USAGE.SNOWFLAKE_INTELLIGENCE_USAGE_HISTORY
        WHERE START_TIME >= {date_filter} AND START_TIME <= {date_filter_end}
        GROUP BY 1 ORDER BY 1
        """
        st.subheader("Daily Trend")
        df_intel_daily = safe_query(intel_daily_sql)
        if not df_intel_daily.empty:
            render_daily_chart(df_intel_daily, "USAGE_DATE", "CREDITS")

        st.subheader("Intelligence Details")
        st.dataframe(df_intel.reset_index(drop=True))
    else:
        st.info("No Snowflake Intelligence usage found for the selected period.")

# ============================
# TAB: Document AI
# ============================
with tabs[8]:
    st.header("Document AI")
    st.caption("Document AI usage for extracting structured data from documents.")

    docai_sql = f"""
    SELECT
        OPERATION_NAME,
        ROUND(SUM(CREDITS_USED), 4) AS CREDITS,
        SUM(PAGE_COUNT) AS TOTAL_PAGES,
        SUM(DOCUMENT_COUNT) AS TOTAL_DOCUMENTS,
        COUNT(*) AS OPERATIONS
    FROM SNOWFLAKE.ACCOUNT_USAGE.DOCUMENT_AI_USAGE_HISTORY
    WHERE START_TIME >= {date_filter} AND START_TIME <= {date_filter_end}
    GROUP BY OPERATION_NAME
    ORDER BY CREDITS DESC
    """
    df_docai = safe_query(docai_sql)
    if not df_docai.empty:
        total_creds = df_docai["CREDITS"].sum()
        total_pages = df_docai["TOTAL_PAGES"].sum()
        total_docs = df_docai["TOTAL_DOCUMENTS"].sum()
        k1, k2, k3 = st.columns(3)
        k1.metric("Total Credits", format_credits(total_creds))
        k2.metric("Pages Processed", f"{total_pages:,.0f}")
        k3.metric("Documents Processed", f"{total_docs:,.0f}")

        docai_daily_sql = f"""
        SELECT DATE(START_TIME) AS USAGE_DATE, ROUND(SUM(CREDITS_USED), 4) AS CREDITS
        FROM SNOWFLAKE.ACCOUNT_USAGE.DOCUMENT_AI_USAGE_HISTORY
        WHERE START_TIME >= {date_filter} AND START_TIME <= {date_filter_end}
        GROUP BY 1 ORDER BY 1
        """
        st.subheader("Daily Trend")
        df_docai_daily = safe_query(docai_daily_sql)
        if not df_docai_daily.empty:
            render_daily_chart(df_docai_daily, "USAGE_DATE", "CREDITS")

        st.subheader("Operation Breakdown")
        df_table = df_docai.rename(columns={"OPERATION_NAME": "Operation", "CREDITS": "Credits", "TOTAL_PAGES": "Pages", "TOTAL_DOCUMENTS": "Documents", "OPERATIONS": "Operations"}).reset_index(drop=True)
        st.dataframe(df_table)
    else:
        st.info("No Document AI usage found for the selected period.")
