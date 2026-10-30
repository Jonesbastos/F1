"""Provedor de dados para o Dashboard lendo a camada analítica Parquet com fallback."""

from pathlib import Path
from typing import Any

import pandas as pd

from f1.config.settings import Settings, get_settings
from f1.utils.logger import get_logger

logger = get_logger("f1.dashboard.data_provider")


class DashboardDataProvider:
    """Carrega dados persistidos no Data Lake analítico para exibição no Dashboard.

    Caso o Data Lake ainda não tenha sido populado pela execução de pipelines,
    fornece dados demonstrativos realistas da Fórmula 1 para garantir visualização
    imediata e consistente no Dashboard.

    Attributes:
        base_dir: Diretório raiz dos datasets Parquet.
    """

    def __init__(
        self,
        base_dir: Path | str | None = None,
        settings: Settings | None = None,
    ) -> None:
        """Inicializa o provedor de dados com o diretório configurado.

        Args:
            base_dir: Caminho base para leitura. Se omitido, utiliza DATA_OUTPUT_DIR dos settings.
            settings: Instância de configurações.
        """
        cfg = settings or get_settings()
        self.base_dir = Path(base_dir) if base_dir is not None else cfg.data_output_dir

    def _read_table(self, table_name: str) -> pd.DataFrame:
        """Lê com segurança uma tabela ou partição Parquet caso ela exista em disco.

        Args:
            table_name: Nome do diretório/tabela (ex: 'sessions', 'laps').

        Returns:
            DataFrame contendo os dados, ou DataFrame vazio se não existir ou houver falha.
        """
        target_path = self.base_dir / table_name
        if not target_path.exists():
            # Tenta também como arquivo direto table_name.parquet
            file_path = self.base_dir / f"{table_name}.parquet"
            if file_path.exists():
                target_path = file_path
            else:
                return pd.DataFrame()

        try:
            return pd.read_parquet(target_path)
        except Exception as exc:
            logger.warning("Falha ao ler conjunto de dados '%s': %s", table_name, exc)
            return pd.DataFrame()

    def is_demo_mode(self) -> bool:
        """Indica se o dashboard está operando em modo demonstração (dados ausentes).

        Returns:
            True se o Data Lake local estiver vazio; False caso contrário.
        """
        df_sessions = self._read_table("sessions")
        return df_sessions.empty

    def get_overview_stats(self) -> dict[str, Any]:
        """Obtém contadores gerais de volumetria armazenada no Data Lake.

        Returns:
            Dicionário com a quantidade total de registros por entidade.
        """
        meetings_len = len(self._read_table("meetings"))
        sessions_len = len(self._read_table("sessions"))
        drivers_len = len(self._read_table("drivers"))
        laps_len = len(self._read_table("laps"))
        telemetry_len = len(self._read_table("telemetry"))

        is_demo = sessions_len == 0 and meetings_len == 0

        if is_demo:
            return {
                "meetings": 1,
                "sessions": 1,
                "drivers": 5,
                "laps": 24,
                "pit_stops": 6,
                "telemetry": 120,
                "weather": 15,
                "race_control": 4,
                "is_demo": True,
            }

        return {
            "meetings": meetings_len,
            "sessions": sessions_len,
            "drivers": drivers_len,
            "laps": laps_len,
            "pit_stops": len(self._read_table("pit_stops")),
            "telemetry": telemetry_len,
            "weather": len(self._read_table("weather")),
            "race_control": len(self._read_table("race_control")),
            "is_demo": False,
        }

    def get_meetings(self) -> list[dict[str, Any]]:
        """Retorna os Grandes Prêmios e reuniões registradas.

        Returns:
            Lista de dicionários formatados das reuniões.
        """
        df = self._read_table("meetings")
        if df.empty:
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
                    "date_start": "2024-11-03T17:00:00+00:00",
                }
            ]

        if "date_start" in df.columns:
            df["date_start"] = df["date_start"].astype(str)
        return df.to_dict(orient="records")

    def get_sessions(self) -> list[dict[str, Any]]:
        """Retorna as sessões registradas no Data Lake.

        Returns:
            Lista de dicionários das sessões.
        """
        df = self._read_table("sessions")
        if df.empty:
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

        for col in ["date_start", "date_end"]:
            if col in df.columns:
                df[col] = df[col].astype(str)
        return df.to_dict(orient="records")

    def get_drivers(self, session_key: int | None = None) -> list[dict[str, Any]]:
        """Retorna os pilotos registrados, opcionalmente filtrados por sessão.

        Args:
            session_key: Identificador da sessão para filtro.

        Returns:
            Lista de pilotos com metadados de equipe e imagem.
        """
        df = self._read_table("drivers")
        if df.empty:
            demo_drivers = [
                {
                    "driver_number": 1,
                    "broadcast_name": "M VERSTAPPEN",
                    "full_name": "Max Verstappen",
                    "name_acronym": "VER",
                    "team_name": "Red Bull Racing",
                    "team_colour": "3671C6",
                    "headshot_url": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/M/MAXVER01_Max_Verstappen/maxver01.png",
                    "session_key": 9158,
                    "meeting_key": 1219,
                },
                {
                    "driver_number": 4,
                    "broadcast_name": "L NORRIS",
                    "full_name": "Lando Norris",
                    "name_acronym": "NOR",
                    "team_name": "McLaren",
                    "team_colour": "FF8000",
                    "headshot_url": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/L/LANNOR01_Lando_Norris/lannor01.png",
                    "session_key": 9158,
                    "meeting_key": 1219,
                },
                {
                    "driver_number": 44,
                    "broadcast_name": "L HAMILTON",
                    "full_name": "Lewis Hamilton",
                    "name_acronym": "HAM",
                    "team_name": "Mercedes",
                    "team_colour": "27F4D2",
                    "headshot_url": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/L/LEWHAM01_Lewis_Hamilton/lewham01.png",
                    "session_key": 9158,
                    "meeting_key": 1219,
                },
                {
                    "driver_number": 16,
                    "broadcast_name": "C LECLERC",
                    "full_name": "Charles Leclerc",
                    "name_acronym": "LEC",
                    "team_name": "Ferrari",
                    "team_colour": "E80020",
                    "headshot_url": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/C/CHALEC01_Charles_Leclerc/chalec01.png",
                    "session_key": 9158,
                    "meeting_key": 1219,
                },
                {
                    "driver_number": 81,
                    "broadcast_name": "O PIASTRI",
                    "full_name": "Oscar Piastri",
                    "name_acronym": "PIA",
                    "team_name": "McLaren",
                    "team_colour": "FF8000",
                    "headshot_url": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/O/OSCPIA01_Oscar_Piastri/oscpia01.png",
                    "session_key": 9158,
                    "meeting_key": 1219,
                },
            ]
            if session_key is not None:
                return [d for d in demo_drivers if d.get("session_key") == session_key]
            return demo_drivers

        if session_key is not None and "session_key" in df.columns:
            df = df[df["session_key"] == session_key]
        return df.to_dict(orient="records")

    def get_laps(self, session_key: int | None = None, limit: int = 100) -> list[dict[str, Any]]:
        """Retorna registros de voltas cronometradas.

        Args:
            session_key: Filtro opcional por sessão.
            limit: Quantidade máxima de registros retornados.

        Returns:
            Lista de voltas ordenadas.
        """
        df = self._read_table("laps")
        if df.empty:
            return self.get_fastest_laps(session_key=session_key)

        if session_key is not None and "session_key" in df.columns:
            df = df[df["session_key"] == session_key]
        if "date_start" in df.columns:
            df["date_start"] = df["date_start"].astype(str)
        return df.head(limit).to_dict(orient="records")

    def get_fastest_laps(self, session_key: int | None = None) -> list[dict[str, Any]]:
        """Retorna a volta mais rápida por piloto.

        Args:
            session_key: Filtro opcional por sessão.

        Returns:
            Lista de melhores voltas ordenadas por menor tempo.
        """
        df = self._read_table("fastest_laps")
        if df.empty:
            df = self._read_table("laps")
            if not df.empty and "lap_duration" in df.columns:
                df = df.dropna(subset=["lap_duration"])
                if not df.empty:
                    indices = df.groupby("driver_number")["lap_duration"].idxmin()
                    df = df.loc[indices]

        if df.empty:
            return [
                {
                    "driver_number": 1,
                    "lap_number": 68,
                    "lap_duration": 80.472,
                    "duration_sector_1": 23.412,
                    "duration_sector_2": 32.180,
                    "duration_sector_3": 24.880,
                },
                {
                    "driver_number": 4,
                    "lap_number": 65,
                    "lap_duration": 80.890,
                    "duration_sector_1": 23.650,
                    "duration_sector_2": 32.310,
                    "duration_sector_3": 24.930,
                },
                {
                    "driver_number": 16,
                    "lap_number": 67,
                    "lap_duration": 81.120,
                    "duration_sector_1": 23.700,
                    "duration_sector_2": 32.400,
                    "duration_sector_3": 25.020,
                },
                {
                    "driver_number": 44,
                    "lap_number": 64,
                    "lap_duration": 81.345,
                    "duration_sector_1": 23.820,
                    "duration_sector_2": 32.550,
                    "duration_sector_3": 24.975,
                },
                {
                    "driver_number": 81,
                    "lap_number": 66,
                    "lap_duration": 81.410,
                    "duration_sector_1": 23.900,
                    "duration_sector_2": 32.480,
                    "duration_sector_3": 25.030,
                },
            ]

        if session_key is not None and "session_key" in df.columns:
            df = df[df["session_key"] == session_key]
        if "lap_duration" in df.columns:
            df = df.sort_values(by="lap_duration")
        if "date_start" in df.columns:
            df["date_start"] = df["date_start"].astype(str)
        return df.to_dict(orient="records")

    def get_weather(self, session_key: int | None = None) -> list[dict[str, Any]]:
        """Retorna o histórico de condições meteorológicas.

        Args:
            session_key: Filtro opcional por sessão.

        Returns:
            Lista de registros meteorológicos.
        """
        df = self._read_table("weather")
        if df.empty:
            return [
                {
                    "date": "2024-11-03T17:00:00+00:00",
                    "air_temperature": 25.4,
                    "track_temperature": 41.2,
                    "humidity": 62.0,
                    "pressure": 1014.2,
                    "wind_speed": 2.1,
                    "rainfall": 0,
                },
                {
                    "date": "2024-11-03T17:30:00+00:00",
                    "air_temperature": 26.1,
                    "track_temperature": 43.5,
                    "humidity": 60.0,
                    "pressure": 1013.8,
                    "wind_speed": 2.5,
                    "rainfall": 0,
                },
                {
                    "date": "2024-11-03T18:00:00+00:00",
                    "air_temperature": 25.8,
                    "track_temperature": 42.0,
                    "humidity": 64.0,
                    "pressure": 1013.5,
                    "wind_speed": 1.9,
                    "rainfall": 0,
                },
                {
                    "date": "2024-11-03T18:30:00+00:00",
                    "air_temperature": 24.9,
                    "track_temperature": 39.8,
                    "humidity": 68.0,
                    "pressure": 1013.1,
                    "wind_speed": 3.2,
                    "rainfall": 0,
                },
            ]

        if session_key is not None and "session_key" in df.columns:
            df = df[df["session_key"] == session_key]
        if "date" in df.columns:
            df["date"] = df["date"].astype(str)
        return df.to_dict(orient="records")

    def get_telemetry_samples(
        self,
        session_key: int | None = None,
        driver_number: int | None = None,
        limit: int = 150,
    ) -> list[dict[str, Any]]:
        """Retorna uma amostra de telemetria veicular para visualização gráfica.

        Args:
            session_key: Filtro de sessão.
            driver_number: Filtro de piloto.
            limit: Quantidade de amostras.

        Returns:
            Amostra de telemetria ordenada temporalmente.
        """
        df = self._read_table("telemetry")
        if df.empty:
            # Dados demonstrativos de reta e frenagem em Interlagos (Reta dos Boxes -> S do Senna)
            telemetry_points = []
            speeds = [
                160,
                195,
                230,
                265,
                295,
                315,
                328,
                332,
                330,
                290,
                210,
                140,
                110,
                135,
                175,
                215,
                255,
                285,
                305,
                318,
            ]
            throttles = [
                100,
                100,
                100,
                100,
                100,
                100,
                100,
                100,
                80,
                0,
                0,
                0,
                40,
                85,
                100,
                100,
                100,
                100,
                100,
                100,
            ]
            rpms = [
                9500,
                10400,
                11200,
                11800,
                12100,
                12350,
                12450,
                12500,
                12400,
                8500,
                6200,
                5100,
                6500,
                8200,
                9800,
                10900,
                11600,
                12000,
                12250,
                12400,
            ]
            for i in range(len(speeds)):
                sec = i * 2
                telemetry_points.append(
                    {
                        "date": f"2024-11-03T17:10:{sec:02d}+00:00",
                        "speed": speeds[i],
                        "throttle": throttles[i],
                        "rpm": rpms[i],
                        "driver_number": driver_number or 1,
                    }
                )
            return telemetry_points

        if session_key is not None and "session_key" in df.columns:
            df = df[df["session_key"] == session_key]
        if driver_number is not None and "driver_number" in df.columns:
            df = df[df["driver_number"] == driver_number]
        if "date" in df.columns:
            df["date"] = df["date"].astype(str)
        return df.head(limit).to_dict(orient="records")
