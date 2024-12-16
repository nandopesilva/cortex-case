import logging
import os
from datetime import datetime

from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


def load(df, directory="./dags/outputs", file_base_name="dados_demograficos_IBGE"):
    try:
        today = datetime.now().strftime("%Y%m%d")
        file_name = f"{file_base_name}_{today}.csv"

        path = os.path.join(directory, file_name)

        df.to_csv(path, index=False, sep=",", encoding="utf-8")
        postgres_hook = PostgresHook(postgres_conn_id="postgres_default")
        engine = postgres_hook.get_sqlalchemy_engine()
        df.to_sql("case", engine, if_exists="replace", index=False)

    except Exception as e:
        logger.error(f"Error: {e}")
        raise
