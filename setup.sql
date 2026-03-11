/*
 * Snowflake AI Usage Dashboards - Setup Script
 *
 * This script creates all required Snowflake objects and deploys the
 * Streamlit application. Run this in a Snowflake worksheet as ACCOUNTADMIN.
 *
 * Before running:
 *   1. Update COMPUTE_WH below if you want to use a different warehouse.
 *   2. Update the PUT command path to the local path of streamlit_app.py.
 */

-- Use the ACCOUNTADMIN role (required for ACCOUNT_USAGE access)
USE ROLE ACCOUNTADMIN;

-- Create the database and schema
CREATE DATABASE IF NOT EXISTS SNOWFLAKE_AI_USAGE_DASHBOARD;
CREATE SCHEMA IF NOT EXISTS SNOWFLAKE_AI_USAGE_DASHBOARD.PUBLIC;

-- Set context
USE DATABASE SNOWFLAKE_AI_USAGE_DASHBOARD;
USE SCHEMA PUBLIC;

-- Create the stage to hold the Streamlit app files
CREATE STAGE IF NOT EXISTS SNOWFLAKE_AI_USAGE_DASHBOARD.PUBLIC.STREAMLIT_STAGE;

-- Upload the Streamlit application file
-- NOTE: Update the file path below to match your local environment
PUT 'file:///path/to/streamlit_app.py'
    @SNOWFLAKE_AI_USAGE_DASHBOARD.PUBLIC.STREAMLIT_STAGE
    AUTO_COMPRESS=FALSE OVERWRITE=TRUE;

-- Create the Streamlit application
CREATE OR REPLACE STREAMLIT SNOWFLAKE_AI_USAGE_DASHBOARD.PUBLIC.SNOWFLAKE_AI_USAGE_DASHBOARD
    ROOT_LOCATION = '@SNOWFLAKE_AI_USAGE_DASHBOARD.PUBLIC.STREAMLIT_STAGE'
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = 'COMPUTE_WH'
    TITLE = 'Snowflake AI Usage Dashboards';

-- (Optional) Grant access to other roles
-- Replace <role> with the target role name
-- GRANT USAGE ON DATABASE SNOWFLAKE_AI_USAGE_DASHBOARD TO ROLE <role>;
-- GRANT USAGE ON SCHEMA SNOWFLAKE_AI_USAGE_DASHBOARD.PUBLIC TO ROLE <role>;
-- GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE <role>;
-- GRANT USAGE ON STREAMLIT SNOWFLAKE_AI_USAGE_DASHBOARD.PUBLIC.SNOWFLAKE_AI_USAGE_DASHBOARD TO ROLE <role>;
-- GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE <role>;
