import os
from airflow import DAG
from airflow.utils.dates import days_ago
from datetime import timedelta
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
import pandas as pd
import json

os.environ["KAGGLE_CONFIG_DIR"] = "/opt/airflow/keys/"
dir_raw_data = "/opt/airflow/data/raw"
dir_modified_data = "/opt/airflow/data/modified"
kaggle_dataset = "datasnaek/youtube-new"
bucket="de-zoomcamp-project-youtube"

CURRENT_DIR = os.getcwd()
DBT_DIR = CURRENT_DIR + '/dags/dbt/youtube_warehouse'

def transform_csv_files(**kwargs):
    csv_files = [file for file in os.listdir(dir_raw_data) if file.endswith(".csv")]

    for csv_file in csv_files:
        csv_file_path = f'{dir_raw_data}/{csv_file}'

        try:
            df = pd.read_csv(csv_file_path, encoding='utf-8')
        except UnicodeDecodeError:
            encodings = ['latin1', 'ISO-8859-1', 'cp1252']
            for encoding in encodings:
                try:
                    df = pd.read_csv(csv_file_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError("Unable to decode the CSV file with any of the supported encodings.")

        if "tags" in df.columns:
            df.drop(columns=["tags"], inplace=True)

        if "description" in df.columns:
            df.drop(columns=["description"], inplace=True)

        country_code = csv_file[:2]
        df['country'] = country_code
        
        modified_csv_file_path = f'{dir_modified_data}/{csv_file}'
        df.to_csv(modified_csv_file_path, index=False)

def transform_json_files(**kwargs):
    json_files = [file for file in os.listdir(dir_raw_data) if file.endswith(".json")]

    for json_file in json_files:
        json_file_path = f'{dir_raw_data}/{json_file}'

        with open(json_file_path, 'r') as file:
            data = json.load(file)
        
        items = data.get('items', [])

        df = pd.json_normalize(items)

        country_code = json_file[:2]
        df['country'] = country_code

        csv_file_path = f'{dir_modified_data}/{json_file.split(".")[0]}.csv'
        df.to_csv(csv_file_path, index=False)

def upload_to_gcs(**kwargs):
    csv_files = [file for file in os.listdir(dir_modified_data)]

    for csv_file in csv_files:
        csv_file_path = f'{dir_modified_data}/{csv_file}'

        upload_modified = LocalFilesystemToGCSOperator(
            task_id=f"upload_file_{csv_file.replace('.', '_')}",
            src=csv_file_path,
            dst=f"raw/{csv_file}",
            bucket=bucket,
            dag=dag,
        )
        upload_modified.execute(context=kwargs)

def load_videos_to_bigquery(**kwargs):
    load_task = GCSToBigQueryOperator(
        task_id="gcs_to_bigquery",
        bucket=bucket,
        source_objects=["raw/*videos.csv"],
        destination_project_dataset_table="project_dataset.raw_videos",
        write_disposition="WRITE_TRUNCATE",
    )
    load_task.execute(context=kwargs)

def load_category_to_bigquery(**kwargs):
    load_task = GCSToBigQueryOperator(
        task_id="gcs_to_bigquery",
        bucket=bucket,
        source_objects=["raw/*_category_id.csv"],
        destination_project_dataset_table="project_dataset.raw_category",
        write_disposition="WRITE_TRUNCATE",
    )
    load_task.execute(context=kwargs)


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'youtube_analysis_ingestion',
    default_args=default_args,
    description='A DAG to download data from kaggle and load to GCS',
    # schedule_interval=timedelta(days=1),
    schedule_interval=None,
)

start = EmptyOperator(task_id='start', dag=dag)
end = EmptyOperator(task_id='end', dag=dag)

download_dataset = BashOperator(
    task_id="download_dataset",
    bash_command=f"kaggle datasets download {kaggle_dataset} -p {dir_raw_data} --unzip"
)

transform_csv_files = PythonOperator(
    task_id='transform_csv_files',
    python_callable=transform_csv_files,
    provide_context=True,
    dag=dag,
)

transform_json_files = PythonOperator(
    task_id='transform_json_files',
    python_callable=transform_json_files,
    provide_context=True,
    dag=dag,
)

upload_to_gcs = PythonOperator(
    task_id='upload_to_gcs',
    python_callable=upload_to_gcs,
    provide_context=True,
    dag=dag,
)

load_videos_to_bigquery = PythonOperator(
    task_id='load_videos_to_bigquery',
    python_callable=load_videos_to_bigquery,
    provide_context=True,
    dag=dag,
)

load_category_to_bigquery = PythonOperator(
    task_id='load_category_to_bigquery',
    python_callable=load_category_to_bigquery,
    provide_context=True,
    dag=dag,
)

dbt_run = BashOperator(
    dag=dag,
    task_id="dbt_run",
    bash_command=f"cd {DBT_DIR} && dbt run --profiles-dir ."
)

start >> download_dataset >> [transform_csv_files, transform_json_files] >> upload_to_gcs >> [load_videos_to_bigquery, load_category_to_bigquery] >> dbt_run >> end