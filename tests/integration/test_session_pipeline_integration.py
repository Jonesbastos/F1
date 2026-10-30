"""Testes de integração do fluxo completo de sessão com mocks de rede."""

from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import requests

from f1.loaders.parquet_loader import ParquetLoader
from f1.pipelines.session_pipeline import SessionPipeline
from f1.services.openf1_client import OpenF1Client
from f1.utils.rate_limiter import RateLimiter


def test_session_pipeline_integration_flow(
    tmp_path: Path,
    mock_meeting_payload: list[dict],
    mock_session_payload: list[dict],
    mock_driver_payload: list[dict],
    mock_lap_payload: list[dict],
    mock_car_data_payload: list[dict],
    mock_pit_payload: list[dict],
    mock_stints_payload: list[dict],
    mock_weather_payload: list[dict],
    mock_race_control_payload: list[dict],
) -> None:
    """Valida o fluxo integrado de ingestão, transformação e gravação em Parquet."""
    # Arrange
    mock_session = MagicMock(spec=requests.Session)

    def route_mock(url: str, params: dict | None = None, **kwargs):
        resp = MagicMock(spec=requests.Response)
        resp.ok = True
        resp.status_code = 200

        if "/sessions" in url:
            resp.json.return_value = mock_session_payload
        elif "/drivers" in url:
            resp.json.return_value = mock_driver_payload
        elif "/laps" in url:
            resp.json.return_value = mock_lap_payload
        elif "/pit" in url:
            resp.json.return_value = mock_pit_payload
        elif "/stints" in url:
            resp.json.return_value = mock_stints_payload
        elif "/weather" in url:
            resp.json.return_value = mock_weather_payload
        elif "/race_control" in url:
            resp.json.return_value = mock_race_control_payload
        elif "/car_data" in url:
            resp.json.return_value = mock_car_data_payload
        else:
            resp.json.return_value = []

        return resp

    mock_session.get.side_effect = route_mock

    client = OpenF1Client(
        session=mock_session,
        rate_limiter=RateLimiter(rate_per_sec=100.0),
    )
    loader = ParquetLoader(base_dir=tmp_path)
    pipeline = SessionPipeline(client=client, loader=loader)

    # Act
    summary = pipeline.run(session_key=9158, include_telemetry=True)

    # Assert
    assert summary["status"] == "success"
    assert summary["session_key"] == 9158
    assert summary["meeting_key"] == 1219
    assert summary["stats"]["laps"] == 2
    assert summary["stats"]["drivers"] == 2
    assert summary["stats"]["telemetry"] == 2

    # Verificar se as tabelas Parquet foram persistidas
    assert (tmp_path / "sessions").exists()
    assert (tmp_path / "laps").exists()
    assert (tmp_path / "drivers").exists()
    assert (tmp_path / "telemetry").exists()

    # Validação de leitura dos arquivos gerados
    df_laps_saved = pd.read_parquet(tmp_path / "laps")
    assert len(df_laps_saved) == 2
    assert "lap_duration" in df_laps_saved.columns
