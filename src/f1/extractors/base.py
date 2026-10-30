"""Extrator base com suporte a resiliência, retry, rate limit e logging."""

from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from f1.config.settings import Settings, get_settings
from f1.utils.exceptions import OpenF1APIError, RateLimitExceededError
from f1.utils.logger import get_logger
from f1.utils.rate_limiter import RateLimiter

logger = get_logger("f1.extractors.base")


class BaseExtractor:
    """Cliente base de extração com política de retentativa e controle de vazão.

    Attributes:
        settings: Objeto de configurações do projeto.
        rate_limiter: Limitador de requisições por segundo.
        session: Sessão HTTP reutilizável com adaptador de retry.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        rate_limiter: RateLimiter | None = None,
        session: requests.Session | None = None,
    ) -> None:
        """Inicializa o extrator com os parâmetros fornecidos ou padrões.

        Args:
            settings: Configurações da aplicação (obtidas automaticamente se omitidas).
            rate_limiter: Limitador de chamadas (instanciado automaticamente se omitido).
            session: Sessão HTTP customizada (útil para injeção de dependência/testes).
        """
        self.settings = settings or get_settings()
        self.rate_limiter = rate_limiter or RateLimiter(
            rate_per_sec=self.settings.openf1_rate_limit_rps
        )

        if session is not None:
            self.session = session
        else:
            self.session = requests.Session()
            retries = Retry(
                total=self.settings.openf1_max_retries,
                backoff_factor=self.settings.openf1_backoff_factor,
                status_forcelist=[429, 500, 502, 503, 504],
                raise_on_status=False,
            )
            adapter = HTTPAdapter(max_retries=retries)
            self.session.mount("https://", adapter)
            self.session.mount("http://", adapter)

    def get(self, endpoint: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Realiza requisição GET autenticada e limitada à API OpenF1.

        Args:
            endpoint: Caminho relativo do recurso (ex: '/meetings', '/laps').
            params: Dicionário opcional contendo query parameters.

        Returns:
            Lista de dicionários brutos correspondente ao payload JSON.

        Raises:
            RateLimitExceededError: Se a API responder com status HTTP 429.
            OpenF1APIError: Se ocorrer erro na conexão, timeout ou status diferente de 200.
        """
        clean_params = {k: v for k, v in (params or {}).items() if v is not None}
        base_url = self.settings.openf1_base_url.rstrip("/")
        normalized_endpoint = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        url = f"{base_url}{normalized_endpoint}"

        self.rate_limiter.acquire()

        timeout = (self.settings.openf1_timeout_connect, self.settings.openf1_timeout_read)
        logger.debug("Executando requisição GET em %s com params %s", url, clean_params)

        try:
            response = self.session.get(url, params=clean_params, timeout=timeout)
        except requests.exceptions.Timeout as exc:
            msg = f"Tempo limite excedido ao consultar o endpoint {endpoint}: {exc}"
            logger.error(msg)
            raise OpenF1APIError(msg) from exc
        except requests.exceptions.RequestException as exc:
            msg = f"Erro de conexão ao consultar endpoint {endpoint}: {exc}"
            logger.error(msg)
            raise OpenF1APIError(msg) from exc

        if response.status_code == 429:
            msg = f"Rate limit atingido no endpoint {endpoint} (HTTP 429)."
            logger.warning(msg)
            raise RateLimitExceededError(msg, status_code=429)

        if not response.ok:
            msg = f"Falha na requisição {endpoint}: status {response.status_code} - {response.text}"
            logger.error(msg)
            raise OpenF1APIError(msg, status_code=response.status_code)

        try:
            payload = response.json()
            if isinstance(payload, list):
                logger.debug(
                    "Endpoint %s retornou %d registros com sucesso.",
                    endpoint,
                    len(payload),
                )
                return payload
            if isinstance(payload, dict):
                return [payload]
            return []
        except ValueError as exc:
            msg = f"Resposta do endpoint {endpoint} não é um JSON válido: {exc}"
            logger.error(msg)
            raise OpenF1APIError(msg, status_code=response.status_code) from exc
