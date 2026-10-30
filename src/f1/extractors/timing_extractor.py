"""Extrator de cronometragem, voltas, stints, intervalos e paradas nos boxes."""

from typing import Any

from f1.extractors.base import BaseExtractor
from f1.models.lap import Lap
from f1.models.race_events import Interval, PitStop, Position, Stint
from f1.utils.logger import get_logger

logger = get_logger("f1.extractors.timing")


class TimingExtractor(BaseExtractor):
    """Extrator de dados temporais e eventos de corrida da OpenF1 API."""

    def get_laps(
        self,
        session_key: int | str,
        driver_number: int | None = None,
        lap_number: int | None = None,
    ) -> list[Lap]:
        """Obtém as voltas e parciais dos pilotos em uma sessão.

        Args:
            session_key: Identificador da sessão ou 'latest'.
            driver_number: Número de corrida do piloto.
            lap_number: Número específico da volta.

        Returns:
            Lista de objetos Lap validados.
        """
        params: dict[str, Any] = {
            "session_key": session_key,
            "driver_number": driver_number,
            "lap_number": lap_number,
        }
        raw_items = self.get("/laps", params=params)
        laps = [Lap.model_validate(item) for item in raw_items]
        logger.info(
            "Extraídas %d voltas para a sessão %s (driver=%s)",
            len(laps),
            session_key,
            driver_number,
        )
        return laps

    def get_pit_stops(
        self,
        session_key: int | str,
        driver_number: int | None = None,
    ) -> list[PitStop]:
        """Obtém registros de pit stops efetuados durante a sessão.

        Args:
            session_key: Identificador da sessão ou 'latest'.
            driver_number: Número de corrida do piloto.

        Returns:
            Lista de objetos PitStop validados.
        """
        params: dict[str, Any] = {
            "session_key": session_key,
            "driver_number": driver_number,
        }
        raw_items = self.get("/pit", params=params)
        pit_stops = [PitStop.model_validate(item) for item in raw_items]
        logger.info(
            "Extraídos %d pit stops para a sessão %s (driver=%s)",
            len(pit_stops),
            session_key,
            driver_number,
        )
        return pit_stops

    def get_stints(
        self,
        session_key: int | str,
        driver_number: int | None = None,
    ) -> list[Stint]:
        """Obtém o histórico de utilização de compostos de pneus por piloto.

        Args:
            session_key: Identificador da sessão ou 'latest'.
            driver_number: Número de corrida do piloto.

        Returns:
            Lista de objetos Stint validados.
        """
        params: dict[str, Any] = {
            "session_key": session_key,
            "driver_number": driver_number,
        }
        raw_items = self.get("/stints", params=params)
        stints = [Stint.model_validate(item) for item in raw_items]
        logger.info(
            "Extraídos %d stints de pneus para a sessão %s (driver=%s)",
            len(stints),
            session_key,
            driver_number,
        )
        return stints

    def get_intervals(
        self,
        session_key: int | str,
        driver_number: int | None = None,
    ) -> list[Interval]:
        """Obtém os gaps de tempo entre carros e para o líder.

        Args:
            session_key: Identificador da sessão ou 'latest'.
            driver_number: Número de corrida do piloto.

        Returns:
            Lista de objetos Interval validados.
        """
        params: dict[str, Any] = {
            "session_key": session_key,
            "driver_number": driver_number,
        }
        raw_items = self.get("/intervals", params=params)
        intervals = [Interval.model_validate(item) for item in raw_items]
        logger.info(
            "Extraídos %d intervalos para a sessão %s (driver=%s)",
            len(intervals),
            session_key,
            driver_number,
        )
        return intervals

    def get_positions(
        self,
        session_key: int | str,
        driver_number: int | None = None,
    ) -> list[Position]:
        """Obtém as atualizações de posicionamento dos pilotos na pista.

        Args:
            session_key: Identificador da sessão ou 'latest'.
            driver_number: Número de corrida do piloto.

        Returns:
            Lista de objetos Position validados.
        """
        params: dict[str, Any] = {
            "session_key": session_key,
            "driver_number": driver_number,
        }
        raw_items = self.get("/positions", params=params)
        positions = [Position.model_validate(item) for item in raw_items]
        logger.info(
            "Extraídas %d atualizações de posição para a sessão %s (driver=%s)",
            len(positions),
            session_key,
            driver_number,
        )
        return positions
