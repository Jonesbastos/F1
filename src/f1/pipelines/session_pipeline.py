"""Pipeline de ETL completo para processamento analítico de uma sessão de F1."""

from typing import Any

from f1.loaders.parquet_loader import ParquetLoader
from f1.services.openf1_client import OpenF1Client
from f1.transformers.cleaner import (
    clean_laps_dataframe,
    clean_telemetry_dataframe,
    models_to_dataframe,
)
from f1.transformers.race_transformer import (
    compute_pit_stop_metrics,
    compute_stint_metrics,
    extract_fastest_laps,
)
from f1.transformers.telemetry_transformer import (
    compute_telemetry_metrics,
    summarize_driver_telemetry,
)
from f1.utils.logger import get_logger

logger = get_logger("f1.pipelines.session")


class SessionPipeline:
    """Orquestrador do ciclo completo de extração, transformação e carga por sessão.

    Attributes:
        client: Cliente de acesso à API OpenF1.
        loader: Carregador de dados em formato Parquet.
    """

    def __init__(
        self,
        client: OpenF1Client | None = None,
        loader: ParquetLoader | None = None,
    ) -> None:
        """Inicializa o pipeline de sessão.

        Args:
            client: Instância do cliente OpenF1 (ou nova se omitido).
            loader: Instância do carregador Parquet (ou nova se omitido).
        """
        self.client = client or OpenF1Client()
        self.loader = loader or ParquetLoader()

    def run(
        self,
        session_key: int | str = "latest",
        include_telemetry: bool = False,
        telemetry_driver: int | None = None,
    ) -> dict[str, Any]:
        """Executa o pipeline ETL para a sessão especificada.

        Args:
            session_key: Identificador da sessão ou 'latest'.
            include_telemetry: Se True, extrai e processa telemetria veicular (~3.7 Hz).
            telemetry_driver: Piloto alvo para extração de telemetria (se omitido, líderes).

        Returns:
            Dicionário com contadores de volumetria e sumário de execução.
        """
        logger.info("Iniciando pipeline de processamento para a sessão %s", session_key)
        stats: dict[str, int] = {}

        # 1. Extração de sessões
        sessions = self.client.calendar.get_sessions(session_key=session_key)
        df_sessions = models_to_dataframe(sessions)
        if not df_sessions.empty:
            meeting_key = int(df_sessions.iloc[0]["meeting_key"])
            resolved_session_key = int(df_sessions.iloc[0]["session_key"])
        else:
            meeting_key = 0
            resolved_session_key = int(session_key) if str(session_key).isdigit() else 0

        self.loader.write(df_sessions, "sessions")
        stats["sessions"] = len(df_sessions)

        # 2. Pilotos
        drivers = self.client.race_info.get_drivers(session_key=session_key)
        df_drivers = models_to_dataframe(drivers)
        if not df_drivers.empty:
            df_drivers["meeting_key"] = meeting_key
            df_drivers["session_key"] = resolved_session_key
        self.loader.write(df_drivers, "drivers", partition_cols=["session_key"])
        stats["drivers"] = len(df_drivers)

        # 3. Voltas
        laps = self.client.timing.get_laps(session_key=session_key)
        df_laps = clean_laps_dataframe(models_to_dataframe(laps))
        if not df_laps.empty:
            df_laps["meeting_key"] = meeting_key
            df_laps["session_key"] = resolved_session_key
            self.loader.write(df_laps, "laps", partition_cols=["session_key"])
            df_fastest = extract_fastest_laps(df_laps)
            self.loader.write(df_fastest, "fastest_laps", partition_cols=["session_key"])
        stats["laps"] = len(df_laps)

        # 4. Pit Stops e Stints
        pit_stops = self.client.timing.get_pit_stops(session_key=session_key)
        df_pit = models_to_dataframe(pit_stops)
        if not df_pit.empty:
            df_pit["meeting_key"] = meeting_key
            df_pit["session_key"] = resolved_session_key
            self.loader.write(df_pit, "pit_stops", partition_cols=["session_key"])
            df_pit_metrics = compute_pit_stop_metrics(df_pit)
            if not df_pit_metrics.empty:
                df_pit_metrics["meeting_key"] = meeting_key
                df_pit_metrics["session_key"] = resolved_session_key
                self.loader.write(
                    df_pit_metrics, "pit_stop_metrics", partition_cols=["session_key"]
                )
        stats["pit_stops"] = len(df_pit)

        stints = self.client.timing.get_stints(session_key=session_key)
        df_stints = compute_stint_metrics(models_to_dataframe(stints))
        if not df_stints.empty:
            df_stints["meeting_key"] = meeting_key
            df_stints["session_key"] = resolved_session_key
            self.loader.write(df_stints, "stints", partition_cols=["session_key"])
        stats["stints"] = len(df_stints)

        # 5. Clima e Direção de Prova
        weather = self.client.race_info.get_weather(session_key=session_key)
        df_weather = models_to_dataframe(weather)
        if not df_weather.empty:
            df_weather["meeting_key"] = meeting_key
            df_weather["session_key"] = resolved_session_key
            self.loader.write(df_weather, "weather", partition_cols=["session_key"])
        stats["weather"] = len(df_weather)

        race_control = self.client.race_info.get_race_control(session_key=session_key)
        df_race_control = models_to_dataframe(race_control)
        if not df_race_control.empty:
            df_race_control["meeting_key"] = meeting_key
            df_race_control["session_key"] = resolved_session_key
            self.loader.write(df_race_control, "race_control", partition_cols=["session_key"])
        stats["race_control"] = len(df_race_control)

        # 6. Telemetria (opcional com controle de volumetria)
        if include_telemetry:
            car_data = self.client.telemetry.get_car_data(
                session_key=session_key,
                driver_number=telemetry_driver,
            )
            df_telemetry = clean_telemetry_dataframe(models_to_dataframe(car_data))
            if not df_telemetry.empty:
                df_telemetry["meeting_key"] = meeting_key
                df_telemetry["session_key"] = resolved_session_key
                df_telemetry = compute_telemetry_metrics(df_telemetry)
                self.loader.write(
                    df_telemetry,
                    "telemetry",
                    partition_cols=["session_key", "driver_number"],
                )
                df_summary = summarize_driver_telemetry(df_telemetry)
                self.loader.write(df_summary, "telemetry_summary")
            stats["telemetry"] = len(df_telemetry)
        else:
            stats["telemetry"] = 0

        logger.info(
            "Pipeline concluído com sucesso para sessão %s. Estatísticas: %s",
            session_key,
            stats,
        )
        return {
            "session_key": resolved_session_key,
            "meeting_key": meeting_key,
            "stats": stats,
            "status": "success",
        }
