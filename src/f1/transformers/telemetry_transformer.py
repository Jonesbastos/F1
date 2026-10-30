"""Transformações analíticas avançadas para telemetria e posicionamento."""

import pandas as pd

from f1.utils.logger import get_logger

logger = get_logger("f1.transformers.telemetry")


def compute_telemetry_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula derivadas cinemáticas como aceleração aproximada e velocidade média móvel.

    Args:
        df: DataFrame limpo contendo telemetria veicular ordenada por date.

    Returns:
        DataFrame enriquecido com colunas speed_diff e rolling_speed_avg.
    """
    if df.empty or "speed" not in df.columns:
        return df

    enriched = df.copy()

    # Diferença de velocidade instantânea (Proxy de aceleração/frenagem)
    enriched["speed_diff"] = enriched.groupby("driver_number")["speed"].diff()

    # Média móvel da velocidade (janela de 5 amostras ~1.35 segundos)
    enriched["rolling_speed_avg"] = (
        enriched.groupby("driver_number")["speed"]
        .rolling(window=5, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )

    return enriched


def summarize_driver_telemetry(df: pd.DataFrame) -> pd.DataFrame:
    """Gera sumário estatístico de telemetria por piloto para a sessão.

    Args:
        df: DataFrame de telemetria com speed, rpm, throttle.

    Returns:
        DataFrame agregado por driver_number com métricas consolidadas.
    """
    if df.empty or "driver_number" not in df.columns:
        return pd.DataFrame()

    agg_dict: dict[str, list[str]] = {}
    if "speed" in df.columns:
        agg_dict["speed"] = ["max", "mean"]
    if "rpm" in df.columns:
        agg_dict["rpm"] = ["max", "mean"]
    if "throttle" in df.columns:
        agg_dict["throttle"] = ["mean"]

    if not agg_dict:
        return pd.DataFrame()

    summary = df.groupby("driver_number").agg(agg_dict)
    summary.columns = [f"{col}_{func}" for col, func in summary.columns]
    return summary.reset_index()
