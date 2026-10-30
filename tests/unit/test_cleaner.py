"""Testes unitários para regras de limpeza e conformidade temporal."""

from datetime import UTC, datetime

import pandas as pd

from f1.models.meeting import Meeting
from f1.transformers.cleaner import (
    clean_laps_dataframe,
    clean_telemetry_dataframe,
    ensure_utc_datetime,
    models_to_dataframe,
)


def test_ensure_utc_datetime() -> None:
    """Verifica conversão de strings e datetimes para UTC timezone-aware."""
    # String com Z
    dt1 = ensure_utc_datetime("2024-11-03T17:00:00Z")
    assert dt1 is not None
    assert dt1.tzinfo == UTC

    # String com offset
    dt2 = ensure_utc_datetime("2024-11-03T14:00:00-03:00")
    assert dt2 is not None
    assert dt2.tzinfo == UTC
    assert dt2.hour == 17

    # Datetime ingênuo (naive)
    dt_naive = datetime(2024, 11, 3, 17, 0, 0)
    dt3 = ensure_utc_datetime(dt_naive)
    assert dt3 is not None
    assert dt3.tzinfo == UTC

    # Nulo ou inválido
    assert ensure_utc_datetime(None) is None
    assert ensure_utc_datetime("invalid-date-string") is None


def test_models_to_dataframe(mock_meeting_payload: list[dict]) -> None:
    """Verifica conversão de sequência de modelos Pydantic em DataFrame estruturado."""
    # Arrange
    meetings = [Meeting.model_validate(mock_meeting_payload[0])]

    # Act
    df = models_to_dataframe(meetings)

    # Assert
    assert not df.empty
    assert len(df) == 1
    assert "meeting_key" in df.columns
    assert df.iloc[0]["meeting_name"] == "São Paulo Grand Prix"
    assert pd.api.types.is_datetime64_any_dtype(df["date_start"])


def test_clean_telemetry_dataframe() -> None:
    """Verifica filtragem de limites físicos de velocidade, acelerador e marcha."""
    # Arrange
    df_raw = pd.DataFrame(
        [
            {
                "session_key": 9158,
                "driver_number": 1,
                "date": "2024-11-03T17:00:00+00:00",
                "speed": 320,
                "throttle": 100,
                "gear": 8,
            },
            {
                "session_key": 9158,
                "driver_number": 1,
                "date": "2024-11-03T17:00:00+00:00",  # Duplicado
                "speed": 550,  # Físico impossível (>420)
                "throttle": 150,  # Impossível (>100)
                "gear": 10,  # Impossível (>8)
            },
        ]
    )

    # Act
    df_clean = clean_telemetry_dataframe(df_raw)

    # Assert
    assert len(df_clean) == 1
    assert pd.isna(df_clean.iloc[0]["speed"]) or df_clean.iloc[0]["speed"] <= 420


def test_clean_laps_dataframe() -> None:
    """Verifica saneamento de voltas fora de limites e conversão de segmentos."""
    # Arrange
    df_raw = pd.DataFrame(
        [
            {
                "session_key": 9158,
                "driver_number": 1,
                "lap_number": 1,
                "lap_duration": 82.5,
                "duration_sector_1": 25.0,
                "duration_sector_2": 32.0,
                "duration_sector_3": -5.0,  # Inválido negativo
                "segments_sector_1": [2048, 2049],
            },
            {
                "session_key": 9158,
                "driver_number": 1,
                "lap_number": 2,
                "lap_duration": 10.0,  # Inválido (<40s)
                "duration_sector_1": 25.0,
                "duration_sector_2": 32.0,
                "duration_sector_3": 25.0,
                "segments_sector_1": None,
            },
        ]
    )

    # Act
    df_clean = clean_laps_dataframe(df_raw)

    # Assert
    assert len(df_clean) == 2
    assert pd.isna(df_clean.iloc[0]["duration_sector_3"])
    assert pd.isna(df_clean.iloc[1]["lap_duration"])
    assert isinstance(df_clean.iloc[0]["segments_sector_1"], str)
