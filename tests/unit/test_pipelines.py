"""Testes unitários para orquestração de pipelines ETL."""

from pathlib import Path
from unittest.mock import MagicMock

from f1.loaders.parquet_loader import ParquetLoader
from f1.models.meeting import Meeting, Session
from f1.pipelines.historical_pipeline import HistoricalPipeline
from f1.pipelines.session_pipeline import SessionPipeline


def test_session_pipeline_run(tmp_path: Path) -> None:
    """Valida execução completa de SessionPipeline com mocks."""
    # Arrange
    mock_client = MagicMock()
    mock_client.calendar.get_sessions.return_value = [
        Session(
            session_key=9158,
            session_name="Race",
            meeting_key=1219,
            year=2024,
        )
    ]
    mock_client.race_info.get_drivers.return_value = []
    mock_client.timing.get_laps.return_value = []
    mock_client.timing.get_pit_stops.return_value = []
    mock_client.timing.get_stints.return_value = []
    mock_client.race_info.get_weather.return_value = []
    mock_client.race_info.get_race_control.return_value = []
    mock_client.telemetry.get_car_data.return_value = []

    loader = ParquetLoader(base_dir=tmp_path)
    pipeline = SessionPipeline(client=mock_client, loader=loader)

    # Act
    result = pipeline.run(session_key=9158, include_telemetry=True)

    # Assert
    assert result["status"] == "success"
    assert result["session_key"] == 9158
    assert result["meeting_key"] == 1219
    assert "stats" in result


def test_historical_pipeline_run(tmp_path: Path) -> None:
    """Valida orquestração de múltiplas sessões em HistoricalPipeline."""
    # Arrange
    mock_client = MagicMock()
    mock_client.calendar.get_meetings.return_value = [
        Meeting(meeting_key=1219, meeting_name="São Paulo GP", year=2024)
    ]
    mock_client.calendar.get_sessions.return_value = [
        Session(session_key=9158, session_name="Race", meeting_key=1219, year=2024)
    ]
    mock_client.race_info.get_drivers.return_value = []
    mock_client.timing.get_laps.return_value = []
    mock_client.timing.get_pit_stops.return_value = []
    mock_client.timing.get_stints.return_value = []
    mock_client.race_info.get_weather.return_value = []
    mock_client.race_info.get_race_control.return_value = []

    loader = ParquetLoader(base_dir=tmp_path)
    pipeline = HistoricalPipeline(client=mock_client, loader=loader)

    # Act
    summary = pipeline.run(year=2024, country_name="Brazil")

    # Assert
    assert summary["status"] == "success"
    assert summary["meetings_count"] == 1
    assert summary["sessions_processed"] == 1
