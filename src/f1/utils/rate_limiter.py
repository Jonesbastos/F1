"""Módulo utilitário para controle e limitação de taxa de requisições (Rate Limiter)."""

import threading
import time


class RateLimiter:
    """Controlador de taxa de requisições baseado no intervalo mínimo entre chamadas.

    Garante que as requisições não ultrapassem o limite estipulado por segundo
    (ex: ~3 requisições/segundo = intervalo mínimo de ~0.334s).

    Attributes:
        rate_per_sec: Número máximo de chamadas permitidas por segundo.
        interval: Intervalo mínimo em segundos entre duas chamadas consecutivas.
    """

    def __init__(self, rate_per_sec: float = 3.0) -> None:
        """Inicializa o limitador com a taxa configurada.

        Args:
            rate_per_sec: Quantidade máxima de operações por segundo (padrão: 3.0).

        Raises:
            ValueError: Se rate_per_sec for menor ou igual a zero.
        """
        if rate_per_sec <= 0:
            raise ValueError("A taxa por segundo deve ser maior do que zero.")

        self.rate_per_sec = float(rate_per_sec)
        self.interval = 1.0 / self.rate_per_sec
        self._lock = threading.Lock()
        self._last_call = 0.0

    def acquire(self) -> float:
        """Bloqueia a execução até que o intervalo seguro tenha transcorrido.

        Returns:
            Tempo em segundos que a chamada aguardou (0.0 caso não tenha havido espera).
        """
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_call
            wait_time = self.interval - elapsed

            if wait_time > 0:
                time.sleep(wait_time)
                self._last_call = time.monotonic()
                return wait_time

            self._last_call = now
            return 0.0

    def reset(self) -> None:
        """Reinicia o estado interno do limitador."""
        with self._lock:
            self._last_call = 0.0
