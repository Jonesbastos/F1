"""Extrator de telemetria veicular de alta frequência e localização na pista."""

from typing import Any

from f1.extractors.base import BaseExtractor
from f1.models.telemetry import CarData, Location
from f1.utils.logger import get_logger

logger = get_logger("f1.extractors.telemetry")


class TelemetryExtractor(BaseExtractor):
    """Extrator de telemetria analítica (~3.7 Hz) e coordenadas espaciais."""

    def get_car_data(
        self,
        session_key: int | str,
        driver_number: int | None = None,
        speed_gte: int | None = None,
        date_gte: str | None = None,
    ) -> list[CarData]:
        """Obtém medições de telemetria veicular (velocidade, rotação, marcha, pedais).

        Args:
            session_key: Identificador da sessão ou 'latest'.
            driver_number: Número de corrida do piloto.
            speed_gte: Filtro para velocidade maior ou igual a determinado valor em km/h.
            date_gte: Filtro de data inicial em formato ISO 8601.

        Returns:
            Lista de objetos CarData validados.
        """
        params: dict[str, Any] = {"session_key": session_key}
        if driver_number is not None:
            params["driver_number"] = driver_number
        if speed_gte is not None:
            params["speed>="] = speed_gte
        if date_gte is not None:
            params["date>="] = date_gte

        raw_items = self.get("/car_data", params=params)
        car_data = [CarData.model_validate(item) for item in raw_items]
        logger.info(
            "Extraídas %d amostras de telemetria para sessão %s (driver=%s)",
            len(car_data),
            session_key,
            driver_number,
        )
        return car_data

    def get_location(
        self,
        session_key: int | str,
        driver_number: int | None = None,
        date_gte: str | None = None,
    ) -> list[Location]:
        """Obtém coordenadas espaciais 3D (X, Y, Z) dos veículos na pista.

        Args:
            session_key: Identificador da sessão ou 'latest'.
            driver_number: Número de corrida do piloto.
            date_gte: Filtro de data inicial em formato ISO 8601.

        Returns:
            Lista de objetos Location validados.
        """
        params: dict[str, Any] = {"session_key": session_key}
        if driver_number is not None:
            params["driver_number"] = driver_number
        if date_gte is not None:
            params["date>="] = date_gte

        raw_items = self.get("/location", params=params)
        locations = [Location.model_validate(item) for item in raw_items]
        logger.info(
            "Extraídas %d coordenadas de localização para sessão %s (driver=%s)",
            len(locations),
            session_key,
            driver_number,
        )
        return locations
