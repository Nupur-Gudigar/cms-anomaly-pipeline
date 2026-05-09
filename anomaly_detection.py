import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from dotenv import load_dotenv
import os

load_dotenv()

# ── 1. Connect to Snowflake ──────────────────────────────────────────
print("Connecting to Snowflake...")
conn = snowflake.connector.connect(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    role=os.getenv("SNOWFLAKE_ROLE")
)

# ── 2. Load the mart table ───────────────────────────────────────────
print("Loading data from Snowflake...")
query = """
    SELECT
        PRESCRIBER_NPI,
        LAST_NAME,
        FIRST_NAME,
        STATE,
        SPECIALTY,
        TOTAL_CLAIMS,
        TOTAL_DRUG_COST,
        TOTAL_BENEFICIARIES,
        TOTAL_DAY_SUPPLY,
        TOTAL_30DAY_FILLS,
        UNIQUE_DRUGS_PRESCRIBED,
        AVG_COST_PER_CLAIM,
        COST_PER_BENEFICIARY,
        CLAIMS_PER_DRUG
    FROM CMS_MEDICARE.DBT_DEV.FCT_PRESCRIBER_ANOMALY_INPUT
"""
df = pd.read_sql(query, conn)
print(f"Loaded {len(df):,} prescribers")

# ── 3. Select features for the model ────────────────────────────────
features = [
    'TOTAL_CLAIMS',
    'TOTAL_DRUG_COST',
    'TOTAL_BENEFICIARIES',
    'UNIQUE_DRUGS_PRESCRIBED',
    'AVG_COST_PER_CLAIM',
    'COST_PER_BENEFICIARY'
]

X = df[features].fillna(0)

# ── 4. Scale the features ────────────────────────────────────────────
print("Scaling features...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ── 5. Run Isolation Forest ──────────────────────────────────────────
print("Running Isolation Forest...")
model = IsolationForest(
    n_estimators=100,
    contamination=0.005,
    random_state=42
)
df['anomaly_score'] = model.fit_predict(X_scaled)
df['anomaly_score_raw'] = model.score_samples(X_scaled)
df['is_anomaly'] = (df['anomaly_score'] == -1).astype(int)

# ── 6. Summary ───────────────────────────────────────────────────────
total_anomalies = df['is_anomaly'].sum()
anomaly_pct = (total_anomalies / len(df)) * 100
print(f"\nResults:")
print(f"Total prescribers: {len(df):,}")
print(f"Anomalies detected: {total_anomalies:,}")
print(f"Anomaly rate: {anomaly_pct:.2f}%")

print("\nTop 10 most anomalous prescribers:")
top_anomalies = df[df['is_anomaly'] == 1].nsmallest(10, 'anomaly_score_raw')
print(top_anomalies[['LAST_NAME', 'SPECIALTY', 'TOTAL_DRUG_COST',
                       'TOTAL_CLAIMS', 'AVG_COST_PER_CLAIM']].to_string())

# ── 7. Write results back to Snowflake ───────────────────────────────
print("\nWriting results to Snowflake...")
results_df = df[[
    'PRESCRIBER_NPI', 'LAST_NAME', 'FIRST_NAME', 'STATE', 'SPECIALTY',
    'TOTAL_CLAIMS', 'TOTAL_DRUG_COST', 'TOTAL_BENEFICIARIES',
    'UNIQUE_DRUGS_PRESCRIBED', 'AVG_COST_PER_CLAIM',
    'COST_PER_BENEFICIARY', 'anomaly_score_raw', 'is_anomaly'
]].copy()

results_df.columns = [col.upper() for col in results_df.columns]

# Create results schema if needed
conn.cursor().execute("CREATE SCHEMA IF NOT EXISTS CMS_MEDICARE.RESULTS")
conn.cursor().execute("""
    CREATE OR REPLACE TABLE CMS_MEDICARE.RESULTS.ANOMALY_SCORES (
        PRESCRIBER_NPI          VARCHAR,
        LAST_NAME               VARCHAR,
        FIRST_NAME              VARCHAR,
        STATE                   VARCHAR,
        SPECIALTY               VARCHAR,
        TOTAL_CLAIMS            FLOAT,
        TOTAL_DRUG_COST         FLOAT,
        TOTAL_BENEFICIARIES     FLOAT,
        UNIQUE_DRUGS_PRESCRIBED FLOAT,
        AVG_COST_PER_CLAIM      FLOAT,
        COST_PER_BENEFICIARY    FLOAT,
        ANOMALY_SCORE_RAW       FLOAT,
        IS_ANOMALY              INTEGER
    )
""")

write_pandas(
    conn=conn,
    df=results_df,
    table_name="ANOMALY_SCORES",
    schema="RESULTS",
    database="CMS_MEDICARE"
)

print("Done! Results written to CMS_MEDICARE.RESULTS.ANOMALY_SCORES")
conn.close()