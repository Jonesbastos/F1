"""Extrator de Grandes Prêmios e Sessões do calendário de Fórmula 1."""

from typing import Any

from f1.extractors.base import BaseExtractor
from f1.models.meeting import Meeting, Session
from f1.utils.logger import get_logger

logger = get_logger("f1.extractors.calendar")


class CalendarExtractor(BaseExtractor):
    """Extrator responsável pela ingestão de eventos e sessões da Fórmula 1."""

    def get_meetings(
        self,
        year: int | None = None,
        country_name: str | None = None,
        meeting_key: int | str | None = None,
    ) -> list[Meeting]:
        """Obtém a listagem de reuniões/Grandes Prêmios a partir da OpenF1 API.

        Args:
            year: Ano da temporada para filtro.
            country_name: Nome do país do GP (ex: Brazil).
            meeting_key: ID da reunião ou 'latest'.

        Returns:
            Lista de objetos Meeting validados.
        """
        params: dict[str, Any] = {
            "year": year,
            "country_name": country_name,
            "meeting_key": meeting_key,
        }
        raw_items = self.get("/meetings", params=params)
        meetings = [Meeting.model_validate(item) for item in raw_items]
        logger.info("Extraídas %d reuniões com filtros %s", len(meetings), params)
        return meetings

    def get_sessions(
        self,
        meeting_key: int | str | None = None,
        session_key: int | str | None = None,
        session_name: str | None = None,
        year: int | None = None,
    ) -> list[Session]:
        """Obtém a listagem de sessões de pista a partir da OpenF1 API.

        Args:
            meeting_key: ID do evento ou 'latest'.
            session_key: ID único da sessão ou 'latest'.
            session_name: Nome da sessão (ex: Race, Qualifying, Practice 1).
            year: Ano da temporada.

        Returns:
            Lista de objetos Session validados.
        """
        params: dict[str, Any] = {
            "meeting_key": meeting_key,
            "session_key": session_key,
            "session_name": session_name,
            "year": year,
        }
        raw_items = self.get("/sessions", params=params)
        sessions = [Session.model_validate(item) for item in raw_items]
        logger.info("Extraídas %d sessões com filtros %s", len(sessions), params)
        return sessions
