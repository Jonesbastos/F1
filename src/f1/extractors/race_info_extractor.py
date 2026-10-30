"""Extrator de informações de pilotos, clima, direção de prova e rádios."""

from typing import Any

from f1.extractors.base import BaseExtractor
from f1.models.driver import Driver
from f1.models.race_control import RaceControlMessage, TeamRadioRecord, WeatherRecord
from f1.utils.logger import get_logger

logger = get_logger("f1.extractors.race_info")


class RaceInfoExtractor(BaseExtractor):
    """Extrator de metadados periféricos da corrida (pilotos, meteorologia, rádio, comissários)."""

    def get_drivers(
        self,
        session_key: int | str | None = None,
        driver_number: int | None = None,
        meeting_key: int | str | None = None,
    ) -> list[Driver]:
        """Obtém a lista de pilotos participantes da sessão ou evento.

        Args:
            session_key: Identificador da sessão ou 'latest'.
            driver_number: Número de corrida do piloto.
            meeting_key: Identificador do evento pai.

        Returns:
            Lista de objetos Driver validados.
        """
        params: dict[str, Any] = {
            "session_key": session_key,
            "driver_number": driver_number,
            "meeting_key": meeting_key,
        }
        raw_items = self.get("/drivers", params=params)
        drivers = [Driver.model_validate(item) for item in raw_items]
        logger.info("Extraídos %d pilotos com filtros %s", len(drivers), params)
        return drivers

    def get_weather(
        self,
        session_key: int | str,
    ) -> list[WeatherRecord]:
        """Obtém as leituras das condições meteorológicas durante a sessão.

        Args:
            session_key: Identificador da sessão ou 'latest'.

        Returns:
            Lista de objetos WeatherRecord validados.
        """
        params: dict[str, Any] = {"session_key": session_key}
        raw_items = self.get("/weather", params=params)
        weather = [WeatherRecord.model_validate(item) for item in raw_items]
        logger.info(
            "Extraídas %d amostras de clima para a sessão %s",
            len(weather),
            session_key,
        )
        return weather

    def get_race_control(
        self,
        session_key: int | str,
        category: str | None = None,
        flag: str | None = None,
    ) -> list[RaceControlMessage]:
        """Obtém comunicados e bandeiras emitidas pelos comissários de prova da FIA.

        Args:
            session_key: Identificador da sessão ou 'latest'.
            category: Categoria de alerta (Flag, SafetyCar, Drs, Investigation).
            flag: Cor ou status de bandeira (GREEN, YELLOW, RED, CHEQUERED).

        Returns:
            Lista de objetos RaceControlMessage validados.
        """
        params: dict[str, Any] = {
            "session_key": session_key,
            "category": category,
            "flag": flag,
        }
        raw_items = self.get("/race_control", params=params)
        messages = [RaceControlMessage.model_validate(item) for item in raw_items]
        logger.info(
            "Extraídas %d mensagens de race control para sessão %s (flag=%s)",
            len(messages),
            session_key,
            flag,
        )
        return messages

    def get_team_radio(
        self,
        session_key: int | str,
        driver_number: int | None = None,
    ) -> list[TeamRadioRecord]:
        """Obtém o catálogo de áudios de rádio transmitidos entre equipes e pilotos.

        Args:
            session_key: Identificador da sessão ou 'latest'.
            driver_number: Número de corrida do piloto.

        Returns:
            Lista de objetos TeamRadioRecord validados.
        """
        params: dict[str, Any] = {
            "session_key": session_key,
            "driver_number": driver_number,
        }
        raw_items = self.get("/team_radio", params=params)
        radios = [TeamRadioRecord.model_validate(item) for item in raw_items]
        logger.info(
            "Extraídos %d registros de rádio para sessão %s (driver=%s)",
            len(radios),
            session_key,
            driver_number,
        )
        return radios
