"""Testes unitários para validação de esquemas Pydantic."""

from datetime import UTC, datetime

from f1.models.driver import Driver
from f1.models.lap import Lap
from f1.models.meeting import Meeting, Session
from f1.models.race_control import RaceControlMessage, TeamRadioRecord, WeatherRecord
from f1.models.race_events import Interval, PitStop, Position, Stint
from f1.models.telemetry import CarData, Location


def test_meeting_model_validation(mock_meeting_payload: list[dict]) -> None:
    """Valida o parsing e tipagem do modelo Meeting."""
    # Arrange & Act
    meeting = Meeting.model_validate(mock_meeting_payload[0])

    # Assert
    assert meeting.meeting_key == 1219
    assert meeting.meeting_name == "São Paulo Grand Prix"
    assert meeting.year == 2024
    assert meeting.country_code == "BRA"
    assert isinstance(meeting.date_start, datetime)


def test_session_model_validation(mock_session_payload: list[dict]) -> None:
    """Valida o parsing e tipagem do modelo Session."""
    # Arrange & Act
    session = Session.model_validate(mock_session_payload[0])

    # Assert
    assert session.session_key == 9158
    assert session.session_name == "Race"
    assert session.meeting_key == 1219
    assert session.year == 2024


def test_driver_model_validation(mock_driver_payload: list[dict]) -> None:
    """Valida o parsing e tipagem do modelo Driver."""
    # Arrange & Act
    driver = Driver.model_validate(mock_driver_payload[0])

    # Assert
    assert driver.driver_number == 1
    assert driver.name_acronym == "VER"
    assert driver.team_name == "Red Bull Racing"


def test_lap_model_validation(mock_lap_payload: list[dict]) -> None:
    """Valida o parsing e tipagem do modelo Lap."""
    # Arrange & Act
    lap = Lap.model_validate(mock_lap_payload[0])

    # Assert
    assert lap.lap_number == 1
    assert lap.driver_number == 1
    assert lap.lap_duration == 82.456
    assert lap.duration_sector_1 == 24.120


def test_telemetry_models_validation(
    mock_car_data_payload: list[dict],
    mock_location_payload: list[dict],
) -> None:
    """Valida o parsing dos modelos CarData e Location."""
    # Arrange & Act
    car_data = CarData.model_validate(mock_car_data_payload[0])
    location = Location.model_validate(mock_location_payload[0])

    # Assert
    assert car_data.speed == 312
    assert car_data.rpm == 11800
    assert car_data.gear == 8
    assert location.x == 1245.5
    assert location.y == -345.2
    assert location.z == 780.0


def test_race_events_models_validation(
    mock_pit_payload: list[dict],
    mock_stints_payload: list[dict],
) -> None:
    """Valida os modelos PitStop, Stint, Position e Interval."""
    # Arrange & Act
    pit = PitStop.model_validate(mock_pit_payload[0])
    stint = Stint.model_validate(mock_stints_payload[0])
    pos = Position(session_key=9158, driver_number=1, position=1)
    inter = Interval(session_key=9158, driver_number=44, gap_to_leader=1.23, interval=0.55)

    # Assert
    assert pit.lap_number == 25
    assert pit.stop_duration == 2.35
    assert stint.compound == "MEDIUM"
    assert pos.position == 1
    assert inter.gap_to_leader == 1.23


def test_race_control_models_validation(
    mock_weather_payload: list[dict],
    mock_race_control_payload: list[dict],
) -> None:
    """Valida os modelos WeatherRecord, RaceControlMessage e TeamRadioRecord."""
    # Arrange & Act
    weather = WeatherRecord.model_validate(mock_weather_payload[0])
    rc = RaceControlMessage.model_validate(mock_race_control_payload[0])
    radio = TeamRadioRecord(
        session_key=9158,
        driver_number=1,
        date=datetime.now(UTC),
        recording_url="https://media.formula1.com/audio.mp3",
    )

    # Assert
    assert weather.air_temperature == 23.5
    assert rc.flag == "GREEN"
    assert radio.recording_url is not None
