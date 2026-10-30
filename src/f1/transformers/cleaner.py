"""Regras puras de limpeza, normalização e conformidade temporal de dados."""

from collections.abc import Sequence
from datetime import UTC, datetime

import pandas as pd
from pydantic import BaseModel

from f1.utils.logger import get_logger

logger = get_logger("f1.transformers.cleaner")


def ensure_utc_datetime(dt: datetime | str | None) -> datetime | None:
    """Garante que um objeto datetime ou string ISO esteja expressamente no fuso UTC.

    Args:
        dt: Datetime ou representação em string ISO 8601.

    Returns:
        Datetime ciente de fuso (timezone-aware) em UTC, ou None se nulo.
    """
    if dt is None:
        return None

    if isinstance(dt, str):
        try:
            # Substitui 'Z' por '+00:00' para compatibilidade ISO
            normalized = dt.replace("Z", "+00:00")
            parsed = datetime.fromisoformat(normalized)
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=UTC)
            return parsed.astimezone(UTC)
        except ValueError as exc:
            logger.warning("Falha ao converter string para datetime UTC: %s (%s)", dt, exc)
            return None

    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            return dt.replace(tzinfo=UTC)
        return dt.astimezone(UTC)

    return None


def models_to_dataframe(models: Sequence[BaseModel]) -> pd.DataFrame:
    """Converte uma sequência de instâncias de modelos Pydantic em um DataFrame Pandas limpo.

    Args:
        models: Sequência iterável de instâncias herdadas de Pydantic BaseModel.

    Returns:
        DataFrame com os registros normalizados.
    """
    if not models:
        return pd.DataFrame()

    records = [m.model_dump(mode="python") for m in models]
    df = pd.DataFrame(records)

    # Converte apenas colunas de data para Datetime UTC padronizado
    for col in df.columns:
        if col in ("date", "date_start", "date_end") or "timestamp" in col:
            try:
                df[col] = pd.to_datetime(df[col], utc=True)
            except Exception as exc:
                logger.debug("Coluna %s não pôde ser convertida para datetime UTC: %s", col, exc)

    return df


def clean_telemetry_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica regras de higienização e validação de limites físicos na telemetria veicular.

    - Filtra valores anômalos de velocidade (< 0 ou > 420 km/h).
    - Assegura que aceleração/throttle esteja na escala 0-100%.
    - Garante que a marcha esteja no intervalo [-1, 8].
    - Remove registros duplicados na mesma estampa de tempo para o mesmo piloto.

    Args:
        df: DataFrame bruto com os dados de telemetria.

    Returns:
        DataFrame saneado e ordenado temporalmente.

    Raises:
        TransformationError: Se o DataFrame de entrada não contiver colunas vitais.
    """
    if df.empty:
        return df

    cleaned = df.copy()

    # Validação de deduplicação temporal
    subset = [col for col in ["session_key", "driver_number", "date"] if col in cleaned.columns]
    if len(subset) == 3:
        cleaned = cleaned.drop_duplicates(subset=subset, keep="last")

    # Tratamento de velocidade
    if "speed" in cleaned.columns:
        cleaned.loc[(cleaned["speed"] < 0) | (cleaned["speed"] > 420), "speed"] = None

    # Tratamento de aceleração / acelerador (0 a 100%)
    if "throttle" in cleaned.columns:
        cleaned.loc[(cleaned["throttle"] < 0) | (cleaned["throttle"] > 100), "throttle"] = None

    # Tratamento de marchas permitidas na F1 (neutro=0, 1 a 8)
    if "gear" in cleaned.columns:
        cleaned.loc[(cleaned["gear"] < 0) | (cleaned["gear"] > 8), "gear"] = None

    if "date" in cleaned.columns:
        cleaned = cleaned.sort_values(by="date").reset_index(drop=True)

    return cleaned


def clean_laps_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Higieniza dados de voltas cronometradas e parciais dos setores.

    - Filtra tempos de volta improváveis (< 40.0s ou > 600.0s).
    - Normaliza tempos negativos de setores.
    - Ordena por piloto e número da volta.

    Args:
        df: DataFrame de voltas.

    Returns:
        DataFrame com registros limpos e consistentes.
    """
    if df.empty:
        return df

    cleaned = df.copy()

    if "lap_duration" in cleaned.columns:
        cleaned.loc[
            (cleaned["lap_duration"] < 40.0) | (cleaned["lap_duration"] > 600.0),
            "lap_duration",
        ] = None

    for sector in ["duration_sector_1", "duration_sector_2", "duration_sector_3"]:
        if sector in cleaned.columns:
            cleaned.loc[cleaned[sector] < 0.0, sector] = None

    # Normalizar campos de segmentos de lista para string ou remover se for nulo
    for seg_col in ["segments_sector_1", "segments_sector_2", "segments_sector_3"]:
        if seg_col in cleaned.columns:
            cleaned[seg_col] = cleaned[seg_col].apply(
                lambda val: str(val) if isinstance(val, list) else None
            )

    sort_cols = [c for c in ["session_key", "driver_number", "lap_number"] if c in cleaned.columns]
    if sort_cols:
        cleaned = cleaned.sort_values(by=sort_cols).reset_index(drop=True)

    return cleaned
