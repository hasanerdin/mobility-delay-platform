from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

dag = DAG(
    dag_id="mobility_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@hourly",
    catchup=False
)

ingestion = BashOperator(
    task_id="run_ingestion",
    bash_command="PYTHONPATH=/opt/airflow/project python /opt/airflow/project/ingestion/run_ingestion.py",
    dag=dag
)

dbt_run = BashOperator(
    task_id="run_dbt",
    bash_command="cd /opt/airflow/project/mobility_dbt && dbt run --profiles-dir .",
    dag=dag
)

dbt_test = BashOperator(
    task_id="run_dbt_tests",
    bash_command="cd /opt/airflow/project/mobility_dbt && dbt test --profiles-dir .",
    dag=dag
)

ingestion >> dbt_run >> dbt_test