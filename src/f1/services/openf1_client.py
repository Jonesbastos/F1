"""Cliente integrado e unificado para a API OpenF1."""

import requests

from f1.config.settings import Settings, get_settings
from f1.extractors.calendar_extractor import CalendarExtractor
from f1.extractors.race_info_extractor import RaceInfoExtractor
from f1.extractors.telemetry_extractor import TelemetryExtractor
from f1.extractors.timing_extractor import TimingExtractor
from f1.utils.rate_limiter import RateLimiter


class OpenF1Client:
    """Gateway unificado que encapsula todos os extratores especializados da OpenF1.

    Compartilha a mesma instância de RateLimiter e sessão HTTP, garantindo
    obediência global ao limite de taxa de ~3 requisições por segundo.

    Attributes:
        settings: Configurações do ambiente e conectividade.
        rate_limiter: Limitador compartilhado de taxa.
        calendar: Extrator de reuniões e sessões.
        timing: Extrator de cronometragem, voltas, stints e boxes.
        telemetry: Extrator de sensores do carro e posicionamento 3D.
        race_info: Extrator de pilotos, clima, diretoria e rádios.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        rate_limiter: RateLimiter | None = None,
        session: requests.Session | None = None,
    ) -> None:
        """Inicializa o cliente com componentes compartilhados.

        Args:
            settings: Configurações da aplicação.
            rate_limiter: Instância de RateLimiter compartilhada.
            session: Sessão HTTP compartilhada.
        """
        self.settings = settings or get_settings()
        self.rate_limiter = rate_limiter or RateLimiter(
            rate_per_sec=self.settings.openf1_rate_limit_rps
        )
        self.session = session or requests.Session()

        self.calendar = CalendarExtractor(
            settings=self.settings,
            rate_limiter=self.rate_limiter,
            session=self.session,
        )
        self.timing = TimingExtractor(
            settings=self.settings,
            rate_limiter=self.rate_limiter,
            session=self.session,
        )
        self.telemetry = TelemetryExtractor(
            settings=self.settings,
            rate_limiter=self.rate_limiter,
            session=self.session,
        )
        self.race_info = RaceInfoExtractor(
            settings=self.settings,
            rate_limiter=self.rate_limiter,
            session=self.session,
        )
