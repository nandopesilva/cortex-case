from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from scripts.extract import collect
from scripts.load import load_csv, load_postgresql
from scripts.transform import transform

AREA_FILE = "./dags/data/AR_BR_RG_UF_RGINT_MES_MIC_MUN_2022.xls"
AREA_SHEET_NAME = "AR_BR_MUN_2022"
AREA_SKIPROWS = 0

POPULATION_FILE = "./dags/data/tabela6579.xlsx"
POPULATION_SHEET_NAME = "Tabela"
POPULATION_SKIPROWS = 3


def __extract_area(**kwargs):
    df = collect(AREA_FILE, AREA_SHEET_NAME, skiprows=AREA_SKIPROWS)
    kwargs["ti"].xcom_push(key="area", value=df)


def __extract_population(**kwargs):
    df = collect(POPULATION_FILE, POPULATION_SHEET_NAME, skiprows=POPULATION_SKIPROWS)
    kwargs["ti"].xcom_push(key="population", value=df)


def __transform(**kwargs):
    df_area = kwargs["ti"].xcom_pull(key="area")
    df_population = kwargs["ti"].xcom_pull(key="population")
    df = transform(df_area, df_population)
    kwargs["ti"].xcom_push(key="transform", value=df)


def __load_csv(**kwargs):
    df = kwargs["ti"].xcom_pull(key="transform")
    execution_date = kwargs['execution_date']
    load_csv(df, execution_date=execution_date)

def __load_postgresql(**kwargs):
    df = kwargs["ti"].xcom_pull(key="transform")
    load_postgresql(df)


with DAG(
    "ibge",
    description="Pipeline de Análise Demográfica com IBGE",
    schedule_interval="@daily",
    start_date=datetime(2024, 12, 1),
    catchup=True,
) as dag:
    task_area = PythonOperator(
        task_id="area",
        python_callable=__extract_area,
        provide_context=True,
    )

    task_population = PythonOperator(
        task_id="population",
        python_callable=__extract_population,
        provide_context=True,
    )

    task_transform = PythonOperator(
        task_id="transform",
        python_callable=__transform,
        provide_context=True,
    )

    task_load_csv = PythonOperator(
        task_id="load_csv",
        python_callable=__load_csv,
        provide_context=True,
    )

    task_load_postgresql = PythonOperator(
        task_id="load_postresql",
        python_callable=__load_postgresql,
        provide_context=True,
    )

    [task_area, task_population] >> task_transform >> [task_load_csv, task_load_postgresql]
