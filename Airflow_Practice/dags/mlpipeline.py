from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def preprocess_data():
  print("We are in the pre processing step")

def train_mode():
  print("We are Training the Model")

def evaluate_model():
  print("Evaluating")

# Define DAG

with DAG(
  'mlpipeline',
  start_date=datetime(2024,1,1),
  schedule='@weekly'
) as dag:
  
  preprocess = PythonOperator(task_id="Preprocessing_taks",python_callable=preprocess_data)
  train = PythonOperator(task_id="Training",python_callable=train_mode)
  evaluate = PythonOperator(task_id="Evaluate", python_callable=evaluate_model)

  # Set Dependencies

  preprocess >> train >> evaluate