"""Fixtures e mocks compartilhados para a suíte de testes Pytest."""

from typing import Any

import pytest


@pytest.fixture
def mock_meeting_payload() -> list[dict[str, Any]]:
    """Payload de exemplo retornado por /meetings."""
    return [
        {
            "meeting_key": 1219,
            "meeting_name": "São Paulo Grand Prix",
            "meeting_code": "BRA",
            "year": 2024,
            "circuit_key": 14,
            "circuit_short_name": "Interlagos",
            "country_name": "Brazil",
            "country_code": "BRA",
            "date_start": "2024-11-01T14:30:00+00:00",
        }
    ]


@pytest.fixture
def mock_session_payload() -> list[dict[str, Any]]:
    """Payload de exemplo retornado por /sessions."""
    return [
        {
            "session_key": 9158,
            "session_name": "Race",
            "session_type": "Race",
            "meeting_key": 1219,
            "year": 2024,
            "date_start": "2024-11-03T17:00:00+00:00",
            "date_end": "2024-11-03T19:00:00+00:00",
            "gmt_offset": "-03:00",
        }
    ]


@pytest.fixture
def mock_driver_payload() -> list[dict[str, Any]]:
    """Payload de exemplo retornado por /drivers."""
    return [
        {
            "driver_number": 1,
            "broadcast_name": "M VERSTAPPEN",
            "full_name": "Max Verstappen",
            "name_acronym": "VER",
            "team_name": "Red Bull Racing",
            "team_colour": "3671C6",
            "headshot_url": "https://media.formula1.com/headshots/verstappen.png",
            "country_code": "NED",
            "session_key": 9158,
            "meeting_key": 1219,
        },
        {
            "driver_number": 44,
            "broadcast_name": "L HAMILTON",
            "full_name": "Lewis Hamilton",
            "name_acronym": "HAM",
            "team_name": "Mercedes",
            "team_colour": "6CD3BF",
            "headshot_url": "https://media.formula1.com/headshots/hamilton.png",
            "country_code": "GBR",
            "session_key": 9158,
            "meeting_key": 1219,
        },
    ]


@pytest.fixture
def mock_lap_payload() -> list[dict[str, Any]]:
    """Payload de exemplo retornado por /laps."""
    return [
        {
            "lap_number": 1,
            "session_key": 9158,
            "driver_number": 1,
            "meeting_key": 1219,
            "lap_duration": 82.456,
            "duration_sector_1": 24.120,
            "duration_sector_2": 32.500,
            "duration_sector_3": 25.836,
            "segments_sector_1": [2048, 2049],
            "segments_sector_2": [2050],
            "segments_sector_3": [2051],
            "is_pit_out_lap": False,
            "date_start": "2024-11-03T17:02:00+00:00",
        },
        {
            "lap_number": 2,
            "session_key": 9158,
            "driver_number": 1,
            "meeting_key": 1219,
            "lap_duration": 80.120,
            "duration_sector_1": 23.900,
            "duration_sector_2": 31.800,
            "duration_sector_3": 24.420,
            "segments_sector_1": [2048],
            "segments_sector_2": [2050],
            "segments_sector_3": [2051],
            "is_pit_out_lap": False,
            "date_start": "2024-11-03T17:03:22+00:00",
        },
    ]


@pytest.fixture
def mock_car_data_payload() -> list[dict[str, Any]]:
    """Payload de exemplo retornado por /car_data."""
    return [
        {
            "session_key": 9158,
            "meeting_key": 1219,
            "driver_number": 1,
            "speed": 312,
            "rpm": 11800,
            "gear": 8,
            "throttle": 100,
            "brake": 0,
            "drs": 12,
            "date": "2024-11-03T17:05:00.100+00:00",
        },
        {
            "session_key": 9158,
            "meeting_key": 1219,
            "driver_number": 1,
            "speed": 315,
            "rpm": 11950,
            "gear": 8,
            "throttle": 100,
            "brake": 0,
            "drs": 12,
            "date": "2024-11-03T17:05:00.370+00:00",
        },
    ]


@pytest.fixture
def mock_location_payload() -> list[dict[str, Any]]:
    """Payload de exemplo retornado por /location."""
    return [
        {
            "session_key": 9158,
            "meeting_key": 1219,
            "driver_number": 1,
            "x": 1245.5,
            "y": -345.2,
            "z": 780.0,
            "date": "2024-11-03T17:05:00.100+00:00",
        }
    ]


@pytest.fixture
def mock_pit_payload() -> list[dict[str, Any]]:
    """Payload de exemplo retornado por /pit."""
    return [
        {
            "session_key": 9158,
            "meeting_key": 1219,
            "driver_number": 1,
            "lap_number": 25,
            "pit_duration": 22.45,
            "stop_duration": 2.35,
            "date": "2024-11-03T17:40:00+00:00",
        }
    ]


@pytest.fixture
def mock_stints_payload() -> list[dict[str, Any]]:
    """Payload de exemplo retornado por /stints."""
    return [
        {
            "session_key": 9158,
            "meeting_key": 1219,
            "driver_number": 1,
            "stint_number": 1,
            "compound": "MEDIUM",
            "tyre_age_at_start": 0,
            "lap_start": 1,
            "lap_end": 25,
        },
        {
            "session_key": 9158,
            "meeting_key": 1219,
            "driver_number": 1,
            "stint_number": 2,
            "compound": "HARD",
            "tyre_age_at_start": 0,
            "lap_start": 26,
            "lap_end": 71,
        },
    ]


@pytest.fixture
def mock_weather_payload() -> list[dict[str, Any]]:
    """Payload de exemplo retornado por /weather."""
    return [
        {
            "session_key": 9158,
            "meeting_key": 1219,
            "date": "2024-11-03T17:00:00+00:00",
            "air_temperature": 23.5,
            "track_temperature": 38.2,
            "humidity": 65.0,
            "pressure": 1012.3,
            "wind_speed": 2.4,
            "wind_direction": 180,
            "rainfall": 0,
        }
    ]


@pytest.fixture
def mock_race_control_payload() -> list[dict[str, Any]]:
    """Payload de exemplo retornado por /race_control."""
    return [
        {
            "session_key": 9158,
            "meeting_key": 1219,
            "date": "2024-11-03T17:00:00+00:00",
            "category": "Flag",
            "flag": "GREEN",
            "scope": "Track",
            "message": "GREEN LIGHT - PIT EXIT OPEN",
            "lap": 1,
            "driver_number": None,
        }
    ]
