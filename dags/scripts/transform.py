import logging

import pandas as pd

logger = logging.getLogger(__name__)


def transform(df_area, df_population):
    try:
        df_area = tranform_area(df_area)

        df_population = transform_population(df_population)

        df_merged = pd.merge(
            df_area, df_population, left_on="CD_MUN", right_on="Cód.", how="inner"
        )

        df_merged.rename(
            columns={
                "NM_MUN": "municipio",
                "NM_UF": "estado",
                "AR_MUN_2022": "area_km2",
                "População": "populacao_municipio",
            },
            inplace=True,
        )

        df_state = (
            df_merged.groupby("estado")["populacao_municipio"].sum().reset_index()
        )
        df_state.rename(
            columns={"populacao_municipio": "populacao_estado"}, inplace=True
        )

        df_final = pd.merge(df_merged, df_state, on="estado", how="left")

        df_final["densidade_populacional"] = (
            df_final["populacao_municipio"] / df_final["area_km2"]
        )
        df_final["percentual_populacao_estado"] = (
            df_final["populacao_municipio"] / df_final["populacao_estado"] * 100
        )

        df_final = df_final[
            [
                "municipio",
                "estado",
                "populacao_municipio",
                "populacao_estado",
                "area_km2",
                "densidade_populacional",
                "percentual_populacao_estado",
            ]
        ]

        df_final.sort_values(by=["estado", "municipio"], inplace=True)

        return df_final

    except Exception as e:
        logger.error(f"Error: {e}")
        raise


def transform_population(df_population):
    df_population.columns = ["Nível", "Cód.", "Reg.", "População", "Unidade"]
    df_population = df_population[["Nível", "Cód.", "Reg.", "População"]].dropna()
    df_population["População"] = pd.to_numeric(
        df_population["População"], errors="coerce"
    )
    df_population = df_population[df_population["Nível"] == "MU"]
    return df_population


def tranform_area(df_area):
    df_area.columns = [
        "ID",
        "CD_UF",
        "NM_UF",
        "NM_UF_SIGLA",
        "CD_MUN",
        "NM_MUN",
        "AR_MUN_2022",
    ]
    df_area = df_area[["CD_UF", "NM_UF", "CD_MUN", "NM_MUN", "AR_MUN_2022"]]
    df_area["AR_MUN_2022"] = (
        df_area["AR_MUN_2022"].replace(",", ".", regex=True).astype(float)
    )
    df_area["AR_MUN_2022"] = pd.to_numeric(df_area["AR_MUN_2022"], errors="coerce")
    return df_area
