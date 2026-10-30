"""Pipeline para ingestão em lote histórica e por temporada completa."""

from typing import Any

from f1.loaders.parquet_loader import ParquetLoader
from f1.pipelines.session_pipeline import SessionPipeline
from f1.services.openf1_client import OpenF1Client
from f1.transformers.cleaner import models_to_dataframe
from f1.utils.logger import get_logger

logger = get_logger("f1.pipelines.historical")


class HistoricalPipeline:
    """Orquestra a ingestão analítica de temporadas completas ou Grandes Prêmios específicos.

    Attributes:
        client: Cliente de acesso à API OpenF1.
        loader: Carregador Parquet.
        session_pipeline: Orquestrador a nível de sessão.
    """

    def __init__(
        self,
        client: OpenF1Client | None = None,
        loader: ParquetLoader | None = None,
    ) -> None:
        """Inicializa o pipeline histórico com injeção de dependências.

        Args:
            client: Cliente OpenF1 unificado.
            loader: Carregador Parquet.
        """
        self.client = client or OpenF1Client()
        self.loader = loader or ParquetLoader()
        self.session_pipeline = SessionPipeline(client=self.client, loader=self.loader)

    def run(
        self,
        year: int,
        country_name: str | None = None,
        include_telemetry: bool = False,
    ) -> dict[str, Any]:
        """Executa a ingestão para todas as reuniões e sessões elegíveis.

        Args:
            year: Temporada a ser ingerida (ex: 2024).
            country_name: Filtro opcional por país (ex: Brazil).
            include_telemetry: Indica se dados de alta frequência devem ser extraídos.

        Returns:
            Dicionário com o sumário da execução por GP e sessão.
        """
        logger.info("Iniciando ingestão histórica para o ano %d (país=%s)", year, country_name)

        # 1. Obter e salvar reuniões do ano
        meetings = self.client.calendar.get_meetings(year=year, country_name=country_name)
        df_meetings = models_to_dataframe(meetings)
        if not df_meetings.empty:
            self.loader.write(df_meetings, "meetings", partition_cols=["year"])

        results: list[dict[str, Any]] = []

        # 2. Iterar por cada GP e processar suas sessões
        for meeting in meetings:
            logger.info("Processando GP %s (key=%s)", meeting.meeting_name, meeting.meeting_key)
            sessions = self.client.calendar.get_sessions(meeting_key=meeting.meeting_key)

            for session in sessions:
                session_result = self.session_pipeline.run(
                    session_key=session.session_key,
                    include_telemetry=include_telemetry,
                )
                results.append(session_result)

        return {
            "year": year,
            "country_name": country_name,
            "meetings_count": len(meetings),
            "sessions_processed": len(results),
            "status": "success",
        }
