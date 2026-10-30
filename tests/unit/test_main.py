"""Testes unitários para a CLI e argumentos de execução (main.py)."""

from unittest.mock import patch

from f1.main import main, parse_arguments
from f1.utils.exceptions import OpenF1APIError


def test_parse_arguments_defaults() -> None:
    """Verifica os valores padrão interpretados pelo parser CLI."""
    # Arrange & Act
    args = parse_arguments([])

    # Assert
    assert args.session_key is None
    assert args.year is None
    assert args.country is None
    assert args.include_telemetry is False
    assert args.telemetry_driver is None


def test_parse_arguments_custom() -> None:
    """Verifica flags e argumentos explícitos na CLI."""
    # Arrange & Act
    args = parse_arguments(
        ["--session-key", "9158", "--include-telemetry", "--telemetry-driver", "1"]
    )

    # Assert
    assert args.session_key == "9158"
    assert args.include_telemetry is True
    assert args.telemetry_driver == 1


@patch("f1.main.SessionPipeline")
def test_main_session_execution(mock_pipe_cls) -> None:
    """Verifica invocação do SessionPipeline pelo main()."""
    # Arrange
    mock_instance = mock_pipe_cls.return_value
    mock_instance.run.return_value = {"status": "success"}

    # Act
    exit_code = main(["--session-key", "9158"])

    # Assert
    assert exit_code == 0
    mock_instance.run.assert_called_once_with(
        session_key="9158",
        include_telemetry=False,
        telemetry_driver=None,
    )


@patch("f1.main.HistoricalPipeline")
def test_main_historical_execution(mock_pipe_cls) -> None:
    """Verifica invocação do HistoricalPipeline quando flag --year é fornecida."""
    # Arrange
    mock_instance = mock_pipe_cls.return_value
    mock_instance.run.return_value = {"status": "success"}

    # Act
    exit_code = main(["--year", "2024", "--country", "Brazil"])

    # Assert
    assert exit_code == 0
    mock_instance.run.assert_called_once_with(
        year=2024,
        country_name="Brazil",
        include_telemetry=False,
    )


@patch("f1.main.SessionPipeline")
def test_main_error_handling(mock_pipe_cls) -> None:
    """Verifica retorno de código 1 caso ocorra exceção controlada na execução."""
    # Arrange
    mock_instance = mock_pipe_cls.return_value
    mock_instance.run.side_effect = OpenF1APIError("Erro de comunicação")

    # Act
    exit_code = main(["--session-key", "9158"])

    # Assert
    assert exit_code == 1
