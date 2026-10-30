"""Testes unitários para o limitador de taxa de requisições."""

import pytest

from f1.utils.rate_limiter import RateLimiter


def test_rate_limiter_initialization() -> None:
    """Verifica se o cálculo do intervalo está correto com base na taxa em segundos."""
    # Arrange & Act
    limiter = RateLimiter(rate_per_sec=2.0)

    # Assert
    assert limiter.rate_per_sec == 2.0
    assert limiter.interval == 0.5


def test_rate_limiter_invalid_rate() -> None:
    """Verifica se valores menores ou iguais a zero lançam ValueError."""
    # Arrange, Act & Assert
    with pytest.raises(ValueError, match="maior do que zero"):
        RateLimiter(rate_per_sec=0.0)

    with pytest.raises(ValueError, match="maior do que zero"):
        RateLimiter(rate_per_sec=-1.0)


def test_rate_limiter_acquire_first_call_no_wait() -> None:
    """Verifica se a primeira chamada ao limiter não impõe espera desnecessária."""
    # Arrange
    limiter = RateLimiter(rate_per_sec=10.0)

    # Act
    wait = limiter.acquire()

    # Assert
    assert wait == 0.0


def test_rate_limiter_acquire_subsequent_call_waits() -> None:
    """Verifica se duas chamadas consecutivas respeitam o intervalo mínimo."""
    # Arrange (taxa alta para teste ágil: 20 req/s -> 0.05s)
    limiter = RateLimiter(rate_per_sec=20.0)

    # Act
    w1 = limiter.acquire()
    w2 = limiter.acquire()

    # Assert
    assert w1 == 0.0
    assert w2 > 0.0


def test_rate_limiter_reset() -> None:
    """Verifica se reset() limpa o estado temporal do limitador."""
    # Arrange
    limiter = RateLimiter(rate_per_sec=1.0)
    limiter.acquire()

    # Act
    limiter.reset()

    # Assert
    assert limiter._last_call == 0.0
