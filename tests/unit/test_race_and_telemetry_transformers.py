"""Testes unitários para cálculos de telemetria e métricas de corrida."""

import pandas as pd

from f1.transformers.race_transformer import (
    compute_pit_stop_metrics,
    compute_stint_metrics,
    extract_fastest_laps,
)
from f1.transformers.telemetry_transformer import (
    compute_telemetry_metrics,
    summarize_driver_telemetry,
)


def test_telemetry_transformer_metrics() -> None:
    """Verifica computação de aceleração aproximada e média móvel."""
    # Arrange
    df = pd.DataFrame(
        [
            {"driver_number": 1, "speed": 100},
            {"driver_number": 1, "speed": 150},
            {"driver_number": 1, "speed": 200},
        ]
    )

    # Act
    enriched = compute_telemetry_metrics(df)

    # Assert
    assert "speed_diff" in enriched.columns
    assert "rolling_speed_avg" in enriched.columns
    assert enriched.iloc[1]["speed_diff"] == 50


def test_summarize_driver_telemetry() -> None:
    """Verifica agregação de valores máximos e médios de telemetria por piloto."""
    # Arrange
    df = pd.DataFrame(
        [
            {"driver_number": 1, "speed": 300, "rpm": 11000, "throttle": 100},
            {"driver_number": 1, "speed": 320, "rpm": 12000, "throttle": 80},
        ]
    )

    # Act
    summary = summarize_driver_telemetry(df)

    # Assert
    assert len(summary) == 1
    assert summary.iloc[0]["speed_max"] == 320
    assert summary.iloc[0]["rpm_max"] == 12000


def test_race_transformer_pit_stops() -> None:
    """Verifica agregação de tempos e quantidades de pit stops."""
    # Arrange
    df_pits = pd.DataFrame(
        [
            {"driver_number": 1, "stop_duration": 2.4, "pit_duration": 21.0},
            {"driver_number": 1, "stop_duration": 2.2, "pit_duration": 20.8},
        ]
    )

    # Act
    metrics = compute_pit_stop_metrics(df_pits)

    # Assert
    assert len(metrics) == 1
    assert metrics.iloc[0]["stop_duration_count"] == 2
    assert metrics.iloc[0]["stop_duration_min"] == 2.2


def test_race_transformer_stints() -> None:
    """Verifica contagem de voltas por stint e cálculo de idade final do pneu."""
    # Arrange
    df_stints = pd.DataFrame(
        [
            {"driver_number": 1, "lap_start": 1, "lap_end": 20, "tyre_age_at_start": 0},
            {"driver_number": 1, "lap_start": 21, "lap_end": 50, "tyre_age_at_start": 3},
        ]
    )

    # Act
    enriched = compute_stint_metrics(df_stints)

    # Assert
    assert enriched.iloc[0]["total_laps"] == 20
    assert enriched.iloc[0]["final_tyre_age"] == 20
    assert enriched.iloc[1]["total_laps"] == 30
    assert enriched.iloc[1]["final_tyre_age"] == 33


def test_extract_fastest_laps() -> None:
    """Verifica seleção da volta mais rápida por piloto."""
    # Arrange
    df_laps = pd.DataFrame(
        [
            {"driver_number": 1, "lap_number": 1, "lap_duration": 85.0},
            {"driver_number": 1, "lap_number": 2, "lap_duration": 81.5},
            {"driver_number": 44, "lap_number": 1, "lap_duration": 82.0},
        ]
    )

    # Act
    fastest = extract_fastest_laps(df_laps)

    # Assert
    assert len(fastest) == 2
    # Verstappen deve ter a volta 2 (81.5)
    ver = fastest[fastest["driver_number"] == 1].iloc[0]
    assert ver["lap_number"] == 2
    assert ver["lap_duration"] == 81.5
