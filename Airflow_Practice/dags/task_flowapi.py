from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.decorators import task
from datetime import datetime
import random
import logging

# Deine The DAG

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 10, 1),
    'retries': 1,
}

with DAG(
    dag_id='task_flow_api_example',
    default_args=default_args,
    description='A simple DAG using TaskFlow API',
    schedule='@once',
    catchup=False,
) as dag:

    @task
    def generate_initial_number():
        logging.info("Generating initial random number")
        initial_number = random.randint(1, 100)
        logging.info(f"Initial number generated: {initial_number}")
        return initial_number

    @task
    def add_five(number):
        logging.info(f"Adding 5 to {number}")
        return number + 5

    @task
    def multiply_by_two(number):
        logging.info(f"Multiplying {number} by 2")
        return number * 2

    @task
    def subtract_three(number):
        logging.info(f"Subtracting 3 from {number}")
        return number - 3

    @task
    def compute_square(number):
        logging.info(f"Computing the square of {number}")
        return number ** 2

    # Define the task dependencies
    initial_number = generate_initial_number()
    added_five = add_five(initial_number)
    multiplied_by_two = multiply_by_two(added_five)
    subtracted_three = subtract_three(multiplied_by_two)
    final_result = compute_square(subtracted_three)