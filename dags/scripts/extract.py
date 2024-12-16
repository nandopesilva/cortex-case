import logging

import pandas as pd

logger = logging.getLogger(__name__)


def collect(file, sheet_name, skiprows=0):
    try:
        df = pd.read_excel(file, sheet_name=sheet_name, skiprows=skiprows)
        return df
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
