# Snowflake AI Usage Dashboards

A Streamlit-in-Snowflake application that provides comprehensive visibility into all Snowflake AI service credit consumption. The dashboard queries `SNOWFLAKE.ACCOUNT_USAGE` views to surface usage metrics across every Snowflake AI service in a single, branded interface.

## Dashboard Tabs

### 1. Overview

Aggregated view of all AI services in your Snowflake account.

| Metric | Description |
|--------|-------------|
| Total AI Credits | Sum of credits consumed across all AI services |
| Active Services | Count of AI services with usage > 0 |

**Visualizations:**
- **Credits by Service** — Horizontal bar chart ranking all services by credit consumption
- **Credit Distribution** — Donut chart showing proportional usage across services
- **Daily AI Credit Usage (All Services)** — Stacked area chart of daily credit trends by service
- **Service Breakdown Table** — Tabular view of all services and their credit totals

### 2. Cortex LLM Functions

Usage of `COMPLETE`, `TRANSLATE`, `SUMMARIZE`, `EXTRACT_ANSWER`, `SENTIMENT`, and other Cortex LLM functions.

| Metric | Description |
|--------|-------------|
| Total Credits | Token credits consumed by LLM functions |
| Total Tokens | Total tokens processed |
| Models Used | Count of distinct LLM models invoked |

**Visualizations:**
- Credits by Model (bar chart)
- Credits by Function (bar chart)
- Daily Trend by Model (stacked area chart)
- Detailed Breakdown table (Function, Model, Credits, Tokens, Usage Hours)

**Source:** `SNOWFLAKE.ACCOUNT_USAGE.CORTEX_FUNCTIONS_USAGE_HISTORY`

### 3. AI SQL Functions

Usage of `AI_COMPLETE`, `AI_EMBED`, `AI_CLASSIFY`, `AI_SUMMARIZE`, and other AI SQL functions.

| Metric | Description |
|--------|-------------|
| Total Credits | Token credits consumed |
| Total Tokens | Total tokens processed |
| Distinct Queries | Count of unique queries using AI SQL functions |

**Visualizations:**
- Credits by Function (bar chart)
- Credits by Model (bar chart)
- Daily Trend by Function (stacked area chart)
- Detailed Breakdown table

**Source:** `SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AISQL_USAGE_HISTORY`

### 4. Cortex Analyst

Natural language to SQL service usage.

| Metric | Description |
|--------|-------------|
| Total Credits | Credits consumed by Cortex Analyst |
| Total Requests | Number of NL-to-SQL requests |
| Active Users | Count of distinct users |
| Avg Credit/Request | Average credit cost per request |

**Visualizations:**
- Credits by User (bar chart)
- Daily Trend (area chart)
- User Breakdown table (User, Credits, Requests, Avg Credit/Req, Active Days)

**Source:** `SNOWFLAKE.ACCOUNT_USAGE.CORTEX_ANALYST_USAGE_HISTORY`

### 5. Cortex Search

Search service usage including indexing and serving costs.

| Metric | Description |
|--------|-------------|
| Total Search Credits | Combined indexing + serving credits |
| Search Services | Count of distinct search services |

**Visualizations:**
- Credits by Service (bar chart)
- Credits by Consumption Type (donut chart — indexing vs. serving)
- Daily Search Trend by Service (stacked area chart)
- Search Service Details table

**Sources:**
- `SNOWFLAKE.ACCOUNT_USAGE.CORTEX_SEARCH_DAILY_USAGE_HISTORY`
- `SNOWFLAKE.ACCOUNT_USAGE.CORTEX_SEARCH_SERVING_USAGE_HISTORY`

### 6. Cortex Code

Cortex Code CLI (AI-powered coding assistant) usage.

| Metric | Description |
|--------|-------------|
| Total Credits | Token credits consumed |
| Total Tokens | Total tokens processed |
| Total Requests | Count of distinct requests |
| Active Users | Count of distinct users |

**Visualizations:**
- Credits by User (bar chart)
- Daily Trend (area chart)
- User Breakdown table

**Source:** `SNOWFLAKE.ACCOUNT_USAGE.CORTEX_CODE_CLI_USAGE_HISTORY`

### 7. Cortex Code UI

Cortex Code Snowsight (AI-powered coding assistant in the Snowflake UI) usage.

| Metric | Description |
|--------|-------------|
| Total Credits | Token credits consumed |
| Total Tokens | Total tokens processed |
| Total Requests | Count of distinct requests |
| Active Users | Count of distinct users |

**Visualizations:**
- Credits by User (bar chart)
- Credit Daily Trend (area chart)
- Tokens by User (bar chart)
- Token Daily Trend (area chart)
- User Breakdown table

**Source:** `SNOWFLAKE.ACCOUNT_USAGE.CORTEX_CODE_SNOWSIGHT_USAGE_HISTORY`

### 8. Cortex Agent

Cortex Agent API usage for building agentic applications.

| Metric | Description |
|--------|-------------|
| Total Credits | Token credits consumed |
| Total Requests | Count of distinct agent requests |
| Active Users | Count of distinct users |
| Agents Used | Count of distinct named agents |

**Visualizations:**
- Credits by User (bar chart)
- Credits by Agent (bar chart)
- Daily Trend by User (stacked area chart)
- Agent Details table

**Source:** `SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AGENT_USAGE_HISTORY`

### 9. Snowflake Intelligence

Snowflake Intelligence (AI-powered analytics assistant) usage.

| Metric | Description |
|--------|-------------|
| Total Credits | Token credits consumed |
| Total Requests | Count of distinct requests |
| Active Users | Count of distinct users |

**Visualizations:**
- Credits by User (bar chart)
- Credits by Intelligence App (bar chart)
- Daily Trend (area chart)
- Intelligence Details table

**Source:** `SNOWFLAKE.ACCOUNT_USAGE.SNOWFLAKE_INTELLIGENCE_USAGE_HISTORY`

### 10. Document AI

Document AI usage for extracting structured data from documents.

| Metric | Description |
|--------|-------------|
| Total Credits | Credits consumed |
| Pages Processed | Total pages analyzed |
| Documents Processed | Total documents analyzed |

**Visualizations:**
- Daily Trend (area chart)
- Operation Breakdown table (Operation, Credits, Pages, Documents, Operations)

**Source:** `SNOWFLAKE.ACCOUNT_USAGE.DOCUMENT_AI_USAGE_HISTORY`

---

## Setup

### Prerequisites

- A Snowflake account with the **ACCOUNTADMIN** role (or a custom role with `IMPORTED PRIVILEGES` on the `SNOWFLAKE` database)
- A virtual warehouse (e.g., `COMPUTE_WH`)

### Quick Start

A complete setup script is provided in [`setup.sql`](setup.sql). To deploy:

1. Open `setup.sql` and update the `PUT` command path to point to your local copy of `streamlit_app.py`.
2. (Optional) Change the warehouse name from `COMPUTE_WH` if needed.
3. Run the entire script in a Snowflake worksheet as **ACCOUNTADMIN**.

The script will:
- Create the `SNOWFLAKE_AI_USAGE_DASHBOARD` database and schema
- Create the internal stage `STREAMLIT_STAGE`
- Upload `streamlit_app.py` to the stage
- Create the Streamlit application

### Open the App

After running the setup script, navigate to **Snowsight > Projects > Streamlit** and open **Snowflake AI Usage Dashboards**, or use the direct URL:

```
https://<your-account>.snowflakecomputing.com/#/streamlit-apps/SNOWFLAKE_AI_USAGE_DASHBOARD.PUBLIC.SNOWFLAKE_AI_USAGE_DASHBOARD
```

### Updating the App

To redeploy after making changes, re-run the `PUT` and `CREATE OR REPLACE STREAMLIT` commands from `setup.sql` (or run the full script again — all statements are idempotent).

---

## Configuration

### Time Period Filter

The sidebar provides a time period selector with the following options:
- Last 7 Days
- Last 30 Days (default)
- Last 90 Days
- Last 180 Days
- Last Year
- Custom — Select a custom "From" and "To" date using date pickers

Preset periods filter data using `DATEADD(DAY, -N, CURRENT_DATE())`. The Custom option uses explicit start and end dates, allowing you to analyze any arbitrary date range.

### Warehouse

The app runs on the warehouse specified in `QUERY_WAREHOUSE` during the `CREATE STREAMLIT` command. Change it by re-creating the Streamlit object with a different warehouse.

### Caching

Query results are cached for **10 minutes** (`@st.cache_data(ttl=600)`). Refreshing the browser page will serve cached data until the TTL expires.

---

## Troubleshooting & FAQ

### No data is showing on any tab

**Cause:** The `SNOWFLAKE.ACCOUNT_USAGE` views require the `ACCOUNTADMIN` role or a role with `IMPORTED PRIVILEGES` on the `SNOWFLAKE` database.

**Fix:** Ensure the Streamlit app is run by a user with the correct role:
```sql
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE <your_role>;
```

### Data appears with a delay

**Expected behavior.** The `SNOWFLAKE.ACCOUNT_USAGE` views have a latency of up to **2 hours**. Recent AI function calls will not appear immediately.

### "No usage found for the selected period" on a specific tab

This simply means there is no recorded usage for that particular AI service in the selected time window. Try extending the time period to "Last 90 Days" or "Last Year".

### AttributeError: module 'streamlit' has no attribute 'connection'

**Cause:** The app is running in Classic Streamlit-in-Snowflake, which uses an older Streamlit runtime.

**Fix:** The app uses `from snowflake.snowpark.context import get_active_session` instead of `st.connection()`. If you see this error, ensure you are using the version of `streamlit_app.py` from this repository.

### AttributeError: module 'streamlit' has no attribute 'column_config'

**Cause:** Same Classic SiS runtime limitation.

**Fix:** The app avoids `st.column_config`, `hide_index`, and other newer Streamlit APIs. Ensure you are using the current version of the app.

### Charts are not rendering

**Possible causes:**
- The queried data is empty (check the time period)
- The warehouse is suspended

**Fix:** Ensure your warehouse is running and try a wider time period.

### Snow CLI deployment fails

If `snow streamlit deploy` fails (e.g., with connection or authentication errors), use the manual SQL deployment method described in the Setup section above.

### How do I grant access to other users?

Grant usage on the database, schema, warehouse, and the Streamlit app:

```sql
GRANT USAGE ON DATABASE SNOWFLAKE_AI_USAGE_DASHBOARD TO ROLE <role>;
GRANT USAGE ON SCHEMA SNOWFLAKE_AI_USAGE_DASHBOARD.PUBLIC TO ROLE <role>;
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE <role>;
GRANT USAGE ON STREAMLIT SNOWFLAKE_AI_USAGE_DASHBOARD.PUBLIC.SNOWFLAKE_AI_USAGE_DASHBOARD TO ROLE <role>;
```

The user's role also needs access to `SNOWFLAKE.ACCOUNT_USAGE`:
```sql
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE <role>;
```

### How do I change the warehouse?

Re-create the Streamlit app with a different `QUERY_WAREHOUSE`:
```sql
CREATE OR REPLACE STREAMLIT SNOWFLAKE_AI_USAGE_DASHBOARD.PUBLIC.SNOWFLAKE_AI_USAGE_DASHBOARD
    ROOT_LOCATION = '@SNOWFLAKE_AI_USAGE_DASHBOARD.PUBLIC.STREAMLIT_STAGE'
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = 'MY_OTHER_WH'
    TITLE = 'Snowflake AI Usage Dashboards';
```

### What ACCOUNT_USAGE views does this app query?

| View | Tab(s) |
|------|--------|
| `CORTEX_FUNCTIONS_USAGE_HISTORY` | Overview, Cortex LLM Functions |
| `CORTEX_AISQL_USAGE_HISTORY` | Overview, AI SQL Functions |
| `CORTEX_ANALYST_USAGE_HISTORY` | Overview, Cortex Analyst |
| `CORTEX_SEARCH_DAILY_USAGE_HISTORY` | Overview, Cortex Search |
| `CORTEX_SEARCH_SERVING_USAGE_HISTORY` | Overview, Cortex Search |
| `CORTEX_CODE_CLI_USAGE_HISTORY` | Overview, Cortex Code CLI |
| `CORTEX_CODE_SNOWSIGHT_USAGE_HISTORY` | Overview, Cortex Code UI |
| `CORTEX_AGENT_USAGE_HISTORY` | Overview, Cortex Agent |
| `SNOWFLAKE_INTELLIGENCE_USAGE_HISTORY` | Overview, Snowflake Intelligence |
| `DOCUMENT_AI_USAGE_HISTORY` | Overview, Document AI |

---

## Project Structure

```
.
├── streamlit_app.py    # Main Streamlit application
├── setup.sql           # SQL setup and deployment script
├── snowflake.yml       # Snow CLI deployment manifest
├── pyproject.toml      # Python project metadata
├── Example_queries.sql # Reference SQL queries
└── README.md           # This file
```
