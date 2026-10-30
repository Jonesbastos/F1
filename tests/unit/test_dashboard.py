"""Testes unitários para o Dashboard e seus endpoints HTTP."""

import json
import threading
from pathlib import Path
from urllib.request import urlopen

import pandas as pd
import pytest

from f1.dashboard.app import create_server
from f1.dashboard.data_provider import DashboardDataProvider
from f1.dashboard.templates import render_dashboard_html


def test_render_dashboard_html() -> None:
    """Verifica se o template HTML é gerado com os elementos principais."""
    # Arrange & Act
    html = render_dashboard_html()

    # Assert
    assert "<!DOCTYPE html>" in html
    assert "F1 Data Platform" in html
    assert "Chart" in html
    assert "/api/stats" in html


def test_data_provider_empty(tmp_path: Path) -> None:
    """Valida retorno demonstrativo do DataProvider quando o diretório estiver vazio."""
    # Arrange
    provider = DashboardDataProvider(base_dir=tmp_path)

    # Act
    stats = provider.get_overview_stats()
    meetings = provider.get_meetings()
    sessions = provider.get_sessions()
    drivers = provider.get_drivers()
    laps = provider.get_laps()
    fastest = provider.get_fastest_laps()
    weather = provider.get_weather()
    telemetry = provider.get_telemetry_samples()

    # Assert
    assert stats["is_demo"] is True
    assert stats["meetings"] > 0
    assert len(meetings) > 0
    assert len(sessions) > 0
    assert len(drivers) > 0
    assert len(laps) > 0
    assert len(fastest) > 0
    assert len(weather) > 0
    assert len(telemetry) > 0


def test_data_provider_populated(tmp_path: Path) -> None:
    """Valida leitura e filtros de DataFrames gravados em Parquet."""
    # Arrange
    provider = DashboardDataProvider(base_dir=tmp_path)

    df_drivers = pd.DataFrame(
        [
            {"driver_number": 1, "session_key": 9158, "full_name": "Max Verstappen"},
            {"driver_number": 44, "session_key": 9159, "full_name": "Lewis Hamilton"},
        ]
    )
    df_drivers.to_parquet(tmp_path / "drivers.parquet")
    # Subdiretório simulando Hive
    drivers_dir = tmp_path / "drivers"
    drivers_dir.mkdir(parents=True, exist_ok=True)
    df_drivers.to_parquet(drivers_dir / "data.parquet")

    # Act
    all_drivers = provider.get_drivers()
    filtered = provider.get_drivers(session_key=9158)

    # Assert
    assert len(all_drivers) == 2
    assert len(filtered) == 1
    assert filtered[0]["driver_number"] == 1


@pytest.fixture
def running_server(tmp_path: Path):
    """Fixture que instancia o servidor HTTP do dashboard em porta aleatória."""
    # Porta 0 faz o OS escolher uma porta livre
    server = create_server(host="127.0.0.1", port=0, data_dir=tmp_path)
    port = server.server_port

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    yield f"http://127.0.0.1:{port}"

    server.shutdown()
    server.server_close()


def test_http_get_dashboard_home(running_server: str) -> None:
    """Verifica resposta 200 da rota principal / com HTML."""
    # Act
    with urlopen(f"{running_server}/") as response:
        status = response.status
        content_type = response.headers.get("Content-Type", "")
        body = response.read().decode("utf-8")

    # Assert
    assert status == 200
    assert "text/html" in content_type
    assert "F1 Data Platform" in body


def test_http_get_api_stats(running_server: str) -> None:
    """Verifica resposta 200 do endpoint /api/stats em JSON."""
    # Act
    with urlopen(f"{running_server}/api/stats") as response:
        status = response.status
        content_type = response.headers.get("Content-Type", "")
        data = json.loads(response.read().decode("utf-8"))

    # Assert
    assert status == 200
    assert "application/json" in content_type
    assert "meetings" in data
    assert "telemetry" in data


def test_http_get_api_routes(running_server: str) -> None:
    """Verifica outros endpoints da API REST."""
    # Act & Assert
    for endpoint in [
        "sessions",
        "meetings",
        "drivers",
        "laps",
        "fastest_laps",
        "weather",
        "telemetry",
    ]:
        with urlopen(f"{running_server}/api/{endpoint}") as response:
            assert response.status == 200
            data = json.loads(response.read().decode("utf-8"))
            assert isinstance(data, list)


def test_http_not_found(running_server: str) -> None:
    """Verifica retorno 404 para rotas inexistentes."""
    import urllib.error

    # Act & Assert
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        urlopen(f"{running_server}/api/rota_inexistente")

    assert exc_info.value.code == 404


def test_http_post_sync(running_server: str) -> None:
    """Verifica acionamento da rota de sincronização /api/sync."""
    import urllib.request

    req = urllib.request.Request(f"{running_server}/api/sync", data=b"", method="POST")
    with urlopen(req) as response:
        assert response.status == 200
        data = json.loads(response.read().decode("utf-8"))
        assert data["status"] == "sync_started"

