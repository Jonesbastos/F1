"""Testes unitários para extratores HTTP da API OpenF1."""

from unittest.mock import MagicMock

import pytest
import requests

from f1.extractors.base import BaseExtractor
from f1.extractors.calendar_extractor import CalendarExtractor
from f1.extractors.race_info_extractor import RaceInfoExtractor
from f1.extractors.telemetry_extractor import TelemetryExtractor
from f1.extractors.timing_extractor import TimingExtractor
from f1.utils.exceptions import OpenF1APIError, RateLimitExceededError
from f1.utils.rate_limiter import RateLimiter


def test_base_extractor_get_success(mock_meeting_payload: list[dict]) -> None:
    """Valida requisição bem-sucedida no BaseExtractor."""
    # Arrange
    mock_session = MagicMock(spec=requests.Session)
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.ok = True
    mock_response.json.return_value = mock_meeting_payload
    mock_session.get.return_value = mock_response

    extractor = BaseExtractor(session=mock_session, rate_limiter=RateLimiter(rate_per_sec=100.0))

    # Act
    data = extractor.get("/meetings")

    # Assert
    assert len(data) == 1
    assert data[0]["meeting_key"] == 1219


def test_base_extractor_rate_limit_429() -> None:
    """Valida lançamento de RateLimitExceededError em caso de HTTP 429."""
    # Arrange
    mock_session = MagicMock(spec=requests.Session)
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 429
    mock_response.ok = False
    mock_session.get.return_value = mock_response

    extractor = BaseExtractor(session=mock_session, rate_limiter=RateLimiter(rate_per_sec=100.0))

    # Act & Assert
    with pytest.raises(RateLimitExceededError):
        extractor.get("/meetings")


def test_base_extractor_http_error() -> None:
    """Valida lançamento de OpenF1APIError quando API responde com status 500."""
    # Arrange
    mock_session = MagicMock(spec=requests.Session)
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 500
    mock_response.ok = False
    mock_response.text = "Internal Server Error"
    mock_session.get.return_value = mock_response

    extractor = BaseExtractor(session=mock_session, rate_limiter=RateLimiter(rate_per_sec=100.0))

    # Act & Assert
    with pytest.raises(OpenF1APIError):
        extractor.get("/meetings")


def test_base_extractor_timeout() -> None:
    """Valida captura de timeout de rede e conversão para OpenF1APIError."""
    # Arrange
    mock_session = MagicMock(spec=requests.Session)
    mock_session.get.side_effect = requests.exceptions.Timeout("Connection timed out")

    extractor = BaseExtractor(session=mock_session, rate_limiter=RateLimiter(rate_per_sec=100.0))

    # Act & Assert
    with pytest.raises(OpenF1APIError, match="Tempo limite excedido"):
        extractor.get("/meetings")


def test_calendar_extractor(
    mock_meeting_payload: list[dict],
    mock_session_payload: list[dict],
) -> None:
    """Valida extração e tipagem em CalendarExtractor."""
    # Arrange
    mock_session = MagicMock(spec=requests.Session)
    mock_response = MagicMock(spec=requests.Response)
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.json.side_effect = [mock_meeting_payload, mock_session_payload]
    mock_session.get.return_value = mock_response

    extractor = CalendarExtractor(
        session=mock_session, rate_limiter=RateLimiter(rate_per_sec=100.0)
    )

    # Act
    meetings = extractor.get_meetings(year=2024, country_name="Brazil")
    sessions = extractor.get_sessions(meeting_key=1219)

    # Assert
    assert len(meetings) == 1
    assert meetings[0].country_name == "Brazil"
    assert len(sessions) == 1
    assert sessions[0].session_name == "Race"


def test_timing_extractor(
    mock_lap_payload: list[dict],
    mock_pit_payload: list[dict],
    mock_stints_payload: list[dict],
) -> None:
    """Valida extração e parsing de voltas, pits e stints em TimingExtractor."""
    # Arrange
    mock_session = MagicMock(spec=requests.Session)
    mock_response = MagicMock(spec=requests.Response)
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.json.side_effect = [
        mock_lap_payload,
        mock_pit_payload,
        mock_stints_payload,
        [{"session_key": 9158, "driver_number": 1, "gap_to_leader": 0.0, "interval": 0.0}],
        [{"session_key": 9158, "driver_number": 1, "position": 1}],
    ]
    mock_session.get.return_value = mock_response

    extractor = TimingExtractor(session=mock_session, rate_limiter=RateLimiter(rate_per_sec=100.0))

    # Act
    laps = extractor.get_laps(session_key=9158)
    pits = extractor.get_pit_stops(session_key=9158)
    stints = extractor.get_stints(session_key=9158)
    intervals = extractor.get_intervals(session_key=9158)
    positions = extractor.get_positions(session_key=9158)

    # Assert
    assert len(laps) == 2
    assert len(pits) == 1
    assert len(stints) == 2
    assert len(intervals) == 1
    assert len(positions) == 1


def test_telemetry_extractor(
    mock_car_data_payload: list[dict],
    mock_location_payload: list[dict],
) -> None:
    """Valida extração de telemetria veicular e coordenadas 3D."""
    # Arrange
    mock_session = MagicMock(spec=requests.Session)
    mock_response = MagicMock(spec=requests.Response)
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.json.side_effect = [mock_car_data_payload, mock_location_payload]
    mock_session.get.return_value = mock_response

    extractor = TelemetryExtractor(
        session=mock_session, rate_limiter=RateLimiter(rate_per_sec=100.0)
    )

    # Act
    car_data = extractor.get_car_data(session_key=9158, driver_number=1, speed_gte=300)
    locations = extractor.get_location(session_key=9158, driver_number=1)

    # Assert
    assert len(car_data) == 2
    assert len(locations) == 1
    assert car_data[0].speed == 312


def test_race_info_extractor(
    mock_driver_payload: list[dict],
    mock_weather_payload: list[dict],
    mock_race_control_payload: list[dict],
) -> None:
    """Valida extração de pilotos, clima, comissários e rádios."""
    # Arrange
    mock_session = MagicMock(spec=requests.Session)
    mock_response = MagicMock(spec=requests.Response)
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.json.side_effect = [
        mock_driver_payload,
        mock_weather_payload,
        mock_race_control_payload,
        [{"session_key": 9158, "driver_number": 1, "date": "2024-11-03T17:00:00+00:00"}],
    ]
    mock_session.get.return_value = mock_response

    extractor = RaceInfoExtractor(
        session=mock_session, rate_limiter=RateLimiter(rate_per_sec=100.0)
    )

    # Act
    drivers = extractor.get_drivers(session_key=9158)
    weather = extractor.get_weather(session_key=9158)
    rc = extractor.get_race_control(session_key=9158)
    radios = extractor.get_team_radio(session_key=9158)

    # Assert
    assert len(drivers) == 2
    assert len(weather) == 1
    assert len(rc) == 1
    assert len(radios) == 1
