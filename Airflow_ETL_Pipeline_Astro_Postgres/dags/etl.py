import json
from h11 import Data
from httpx import post
from datetime import datetime, timedelta
from airflow import DAG
from airflow.decorators import task
from airflow.providers.http.operators.http import HttpOperator as SimpleHttpOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

# Define the DAG

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime.now() - timedelta(days=1),
    "retries": 1,
}

with DAG(
    "etl_dag",
    default_args=default_args,
    description="A simple ETL DAG",
    schedule="@daily",
) as dag:

    # Step 1: Create the table if it does not exist

    @task
    def create_table():
        pg_hook = PostgresHook(
            postgres_conn_id="postgres_default",
        )

        # SQL command to create the table for the API Astronomy Picture of the Day (APOD) data
        create_table_sql = """
		CREATE TABLE IF NOT EXISTS apod_data (
				id SERIAL PRIMARY KEY,
				title VARCHAR(255),
				explanation TEXT,
				url TEXT,
				date DATE,
				media_type VARCHAR(50)
		);
		"""

        # Execute the SQL command
        pg_hook.run(create_table_sql)

    # Step 2: Extract data from the API
    # api_endpoint = 'https://api.nasa.gov/planetary/apod?api_key=2qhSecq7ZVI2TyDgfHGAhblGmrl2Q7ZZHdj1b6Ij'

    extract_apod = SimpleHttpOperator(
        task_id="extract_apod",
        http_conn_id="apod_api",  # Connection ID for the NASA API
        endpoint="planetary/apod",  # Endpoint for the Astronomy Picture of the Day
        method="GET",
        data={
            "api_key": "{{ conn.nasa_api.extra_dejson.api_key }}"
        },  # API key from the connection
        response_filter=lambda response: response.json(),  # Filter to get JSON response
    )

    # Step 3: Transform the data
    @task
    def transform_data(response):
        apod_data = {
            "title": response.get("title", ""),
            "explanation": response.get("explanation", ""),
            "url": response.get("url", ""),
            "date": response.get("date", ""),
            "media_type": response.get("media_type", ""),
        }
        return apod_data

    # Step 4: Load the data into PostgreSQL
    @task
    def load_data_to_postgres(apo_data):
        # Initialize PostgresHook

        pg_hook = PostgresHook(postgres_conn_id="my_postgres_connection")

        # Define SQL Query
        insert_sql = """
        INSERT INTO apod_data (title, explanation, url, date, media_type)
        VALUES (%s, %s, %s, %s, %s);
        """

        # Execute the insert query
        pg_hook.run(
            insert_sql,
            parameters=(
                apo_data["title"],
                apo_data["explanation"],
                apo_data["url"],
                apo_data["date"],
                apo_data["media_type"],
            ),
        )

    # Define the task dependencies

    # Extracting the APOD data and transforming it into a format suitable for PostgreSQL
    create_table_task = create_table() >> extract_apod
    extract_apod_task = extract_apod.output
    # Transforming the data and loading it into PostgreSQL
    transform_data_task = transform_data(extract_apod_task)
    # Loading the transformed data into PostgreSQL
    load_data_to_postgres(transform_data_task)
