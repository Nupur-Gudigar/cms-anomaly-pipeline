import snowflake.connector
import pandas as pd
import json
import os
from dotenv import load_dotenv

load_dotenv()

print("Connecting to Snowflake...")
conn = snowflake.connector.connect(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    role=os.getenv("SNOWFLAKE_ROLE")
)

print("Loading anomaly scores...")
df = pd.read_sql("""
    SELECT
        PRESCRIBER_NPI,
        LAST_NAME,
        FIRST_NAME,
        STATE,
        SPECIALTY,
        TOTAL_CLAIMS,
        TOTAL_DRUG_COST,
        TOTAL_BENEFICIARIES,
        UNIQUE_DRUGS_PRESCRIBED,
        AVG_COST_PER_CLAIM,
        COST_PER_BENEFICIARY,
        ANOMALY_SCORE_RAW,
        IS_ANOMALY
    FROM CMS_MEDICARE.RESULTS.ANOMALY_SCORES
    ORDER BY ANOMALY_SCORE_RAW ASC
""", conn)
conn.close()

df.columns = [col.lower() for col in df.columns]
df = df.fillna(0)

total = len(df)
anomalies = int(df["is_anomaly"].sum())
total_spend = float(df["total_drug_cost"].sum())
anomaly_rate = round((anomalies / total) * 100, 2)

state_counts = (
    df[df["is_anomaly"] == 1]
    .groupby("state")
    .size()
    .reset_index(name="count")
    .sort_values("count", ascending=False)
    .head(15)
    .to_dict(orient="records")
)

specialty_stats = (
    df.groupby("specialty")
    .agg(
        total=("prescriber_npi", "count"),
        anomalies=("is_anomaly", "sum"),
        avg_cost=("avg_cost_per_claim", "mean")
    )
    .reset_index()
)
specialty_stats["anomaly_rate"] = (
    specialty_stats["anomalies"] / specialty_stats["total"] * 100
).round(2)
specialty_stats = (
    specialty_stats[specialty_stats["total"] >= 50]
    .sort_values("anomaly_rate", ascending=False)
    .head(10)
    .to_dict(orient="records")
)

# Only keep columns the dashboard actually needs
slim_cols = [
    "prescriber_npi", "last_name", "first_name", "state", "specialty",
    "total_claims", "total_drug_cost", "avg_cost_per_claim",
    "unique_drugs_prescribed", "total_beneficiaries",
    "anomaly_score_raw", "is_anomaly"
]
prescribers = df[slim_cols].to_dict(orient="records")
for p in prescribers:
    for key in p:
        if isinstance(p[key], float):
            p[key] = round(p[key], 2)

output = {
    "meta": {
        "total_prescribers": total,
        "total_anomalies": anomalies,
        "anomaly_rate": anomaly_rate,
        "total_spend": round(total_spend, 2),
        "data_year": 2023,
        "generated": "2024"
    },
    "state_counts": state_counts,
    "specialty_stats": specialty_stats,
    "prescribers": prescribers
}

with open("docs/data.json", "w") as f:
    json.dump(output, f, separators=(',', ':'))

print(f"Exported {total:,} prescribers to docs/data.json")
print(f"Anomalies: {anomalies} ({anomaly_rate}%)")
print(f"File size: {os.path.getsize('docs/data.json') / 1024 / 1024:.1f} MB")