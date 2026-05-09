from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import os

# ── Default settings for all tasks ──────────────────────────────────
default_args = {
    'owner': 'nupur',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

# ── Define the DAG ───────────────────────────────────────────────────
with DAG(
    dag_id='cms_medicare_anomaly_pipeline',
    default_args=default_args,
    description='End-to-end Medicare Part D anomaly detection pipeline',
    schedule_interval='@weekly',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['cms', 'medicare', 'anomaly-detection']
) as dag:

    # ── Task 1: Run dbt models ───────────────────────────────────────
    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='cd /opt/airflow/cms_medicare && dbt run --profiles-dir /opt/airflow/cms_medicare',
    )

    # ── Task 2: Run dbt tests ────────────────────────────────────────
    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='cd /opt/airflow/cms_medicare && dbt test --profiles-dir /opt/airflow/cms_medicare',
    )

    # ── Task 3: Run anomaly detection ────────────────────────────────
    anomaly_detection = BashOperator(
        task_id='anomaly_detection',
        bash_command='cd /opt/airflow && python anomaly_detection.py',
    )

    # ── Task 4: Run data quality checks ─────────────────────────────
    quality_checks = BashOperator(
        task_id='great_expectations_checks',
        bash_command='cd /opt/airflow && python data_quality_checks.py',
    )

    # ── Define the order ─────────────────────────────────────────────
    dbt_run >> dbt_test >> anomaly_detection >> quality_checks