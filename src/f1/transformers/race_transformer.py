"""Transformadores analíticos e agregações para eventos de corrida."""

import pandas as pd

from f1.utils.logger import get_logger

logger = get_logger("f1.transformers.race")


def compute_pit_stop_metrics(df_pit: pd.DataFrame) -> pd.DataFrame:
    """Calcula estatísticas de desempenho dos pit stops por piloto e equipe.

    Args:
        df_pit: DataFrame contendo registros de pit stops com stop_duration e pit_duration.

    Returns:
        DataFrame agregado com média e menor tempo de parada por piloto.
    """
    if df_pit.empty or "driver_number" not in df_pit.columns:
        return pd.DataFrame()

    agg_targets: dict[str, list[str]] = {}
    if "stop_duration" in df_pit.columns:
        agg_targets["stop_duration"] = ["count", "min", "mean"]
    if "pit_duration" in df_pit.columns:
        agg_targets["pit_duration"] = ["min", "mean"]

    if not agg_targets:
        return pd.DataFrame()

    summary = df_pit.groupby("driver_number").agg(agg_targets)
    summary.columns = [f"{col}_{func}" for col, func in summary.columns]
    return summary.reset_index()


def compute_stint_metrics(df_stints: pd.DataFrame) -> pd.DataFrame:
    """Calcula a extensão em voltas e degradação estimada de pneus por stint.

    Args:
        df_stints: DataFrame com colunas lap_start, lap_end, compound, tyre_age_at_start.

    Returns:
        DataFrame enriquecido com total_laps e final_tyre_age.
    """
    if df_stints.empty:
        return df_stints

    enriched = df_stints.copy()

    if "lap_start" in enriched.columns and "lap_end" in enriched.columns:
        enriched["total_laps"] = enriched["lap_end"] - enriched["lap_start"] + 1

    if "tyre_age_at_start" in enriched.columns and "total_laps" in enriched.columns:
        enriched["final_tyre_age"] = enriched["tyre_age_at_start"].fillna(0) + enriched[
            "total_laps"
        ].fillna(0)

    return enriched


def extract_fastest_laps(df_laps: pd.DataFrame) -> pd.DataFrame:
    """Identifica a volta mais rápida de cada piloto na sessão.

    Args:
        df_laps: DataFrame de voltas com colunas driver_number e lap_duration.

    Returns:
        DataFrame contendo a melhor volta de cada piloto ordenado pelo menor tempo.
    """
    if df_laps.empty or "lap_duration" not in df_laps.columns:
        return pd.DataFrame()

    valid_laps = df_laps.dropna(subset=["lap_duration"])
    if valid_laps.empty:
        return pd.DataFrame()

    fastest_indices = valid_laps.groupby("driver_number")["lap_duration"].idxmin()
    best_laps = valid_laps.loc[fastest_indices].sort_values(by="lap_duration")
    return best_laps.reset_index(drop=True)
