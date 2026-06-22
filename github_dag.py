from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from x_etl import run_etl

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2020, 11, 8),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

dag = DAG(
    'github_etl_dag',
    default_args=default_args,
    description='A simple ETL DAG to extract GitHub repo data',
    schedule="@daily",
)   

run_etl_task = PythonOperator(
    task_id='run_etl',
    python_callable=run_etl,
    dag=dag,
)
run_etl_task