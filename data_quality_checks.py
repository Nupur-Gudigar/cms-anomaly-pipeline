import great_expectations as gx
import pandas as pd
import snowflake.connector
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

# ── 2. Load anomaly results ──────────────────────────────────────────
print("Loading anomaly scores...")
query = """
    SELECT
        PRESCRIBER_NPI,
        IS_ANOMALY,
        ANOMALY_SCORE_RAW,
        TOTAL_DRUG_COST,
        TOTAL_CLAIMS
    FROM CMS_MEDICARE.RESULTS.ANOMALY_SCORES
"""
df = pd.read_sql(query, conn)
conn.close()
print(f"Loaded {len(df):,} rows")

# ── 3. Set up Great Expectations ─────────────────────────────────────
print("Running data quality checks...")
context = gx.get_context()
data_source = context.data_sources.add_pandas("anomaly_results")
data_asset = data_source.add_dataframe_asset("scores")
batch_definition = data_asset.add_batch_definition_whole_dataframe("batch")
batch = batch_definition.get_batch(batch_parameters={"dataframe": df})

# ── 4. Define Expectations ───────────────────────────────────────────
suite = context.suites.add(
    gx.ExpectationSuite(name="anomaly_quality_suite")
)

# Expectation 1: IS_ANOMALY only contains 0 or 1
suite.add_expectation(
    gx.expectations.ExpectColumnDistinctValuesToBeInSet(
        column="IS_ANOMALY",
        value_set=[0, 1]
    )
)

# Expectation 2: No null prescriber NPIs
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToNotBeNull(
        column="PRESCRIBER_NPI"
    )
)

# Expectation 3: Anomaly rate must not exceed 0.5%
total = len(df)
anomaly_count = df["IS_ANOMALY"].sum()
anomaly_rate = anomaly_count / total

suite.add_expectation(
    gx.expectations.ExpectColumnMeanToBeBetween(
        column="IS_ANOMALY",
        min_value=0.0,
        max_value=0.006
    )
)

# Expectation 4: Drug costs must be positive
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeBetween(
        column="TOTAL_DRUG_COST",
        min_value=0
    )
)

# ── 5. Run Validation ────────────────────────────────────────────────
validation_definition = context.validation_definitions.add(
    gx.ValidationDefinition(
        name="anomaly_validation",
        data=batch_definition,
        suite=suite
    )
)

results = validation_definition.run(
    batch_parameters={"dataframe": df}
)

# ── 6. Print Results ─────────────────────────────────────────────────
print("\n" + "="*50)
print("GREAT EXPECTATIONS RESULTS")
print("="*50)
print(f"Overall success: {results.success}")
print(f"Anomaly rate: {anomaly_rate:.4%}")
print(f"Total prescribers: {total:,}")
print(f"Flagged as anomalous: {anomaly_count:,}")
print("="*50)

for result in results.results:
    status = "✅ PASS" if result.success else "❌ FAIL"
    print(f"{status} → {result.expectation_config.type}")

if not results.success:
    raise Exception("Data quality checks failed! Pipeline stopped.")
else:
    print("\nAll quality checks passed! Safe to proceed.")