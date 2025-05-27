"""

We'll define DAGs for the following tasks:

1. Start with Initail Number
2. Add 5 to the number
3. Multiply the number by 2
4. Subtract 3 from the number
5. Compute the square of the number

"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import random
import logging

# Function to generate a random initial number
def generate_initial_number(**context):
    logging.info("Generating initial random number")
    initial_number = random.randint(1, 100)
    logging.info(f"Initial number generated: {initial_number}")
    # Push the initial number to XCom
    context['ti'].xcom_push(key='initial_number', value=initial_number)

# Function to add 5 to the number
def add_five(**context):
    number = context['ti'].xcom_pull(key='initial_number', task_ids='start_with_initial_number')
    logging.info(f"Adding 5 to {number}")
    context['ti'].xcom_push(key='add_five', value=number + 5)

# Function to multiply the number by 2
def multiply_by_two(**context):
    number = context['ti'].xcom_pull(key='add_five', task_ids='add_five')
    logging.info(f"Multiplying {number} by 2")
    context['ti'].xcom_push(key='multiply_by_two', value=number * 2)

# Function to subtract 3 from the number
def subtract_three(**context):
    number = context['ti'].xcom_pull(key='multiply_by_two', task_ids='multiply_by_two')
    logging.info(f"Subtracting 3 from {number}")
    context['ti'].xcom_push(key='subtract_three', value=number - 3)

# Function to compute the square of the number
def compute_square(**context):
    number = context['ti'].xcom_pull(key='subtract_three', task_ids='subtract_three')
    logging.info(f"Computing the square of {number}")
    context['ti'].xcom_push(key='compute_square', value=number ** 2)

# Define the DAG

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 10, 1),
    'retries': 1,
}

with DAG(
    'math_operations_dag',
    default_args=default_args,
    description='A simple DAG to perform math operations',
    schedule='@once',  # Set to None for manual triggering
) as dag:

    # Task 1: Generate initial number
    generate_number_task = PythonOperator(
        task_id='start_with_initial_number',
        python_callable=generate_initial_number,
    )

    # Task 2: Add 5 to the number
    add_five_task = PythonOperator(
        task_id='add_five',
        python_callable=add_five,
    )
    # Task 3: Multiply the number by 2
    multiply_by_two_task = PythonOperator(
        task_id='multiply_by_two',
        python_callable=multiply_by_two,
    )
    # Task 4: Subtract 3 from the number
    subtract_three_task = PythonOperator(
        task_id='subtract_three',
        python_callable=subtract_three,
    )
    # Task 5: Compute the square of the number
    compute_square_task = PythonOperator(
        task_id='compute_square',
        python_callable=compute_square,
    )
    # Set task dependencies
    generate_number_task >> add_five_task >> multiply_by_two_task >> subtract_three_task >> compute_square_task
# End of DAG definition