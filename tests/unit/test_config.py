"""Testes unitários para configurações e variáveis de ambiente."""

from pathlib import Path

from f1.config.settings import Settings, get_settings


def test_settings_default_values() -> None:
    """Valida se os valores padrão de Settings respeitam os requisitos da plataforma."""
    # Arrange & Act
    settings = Settings()

    # Assert
    assert settings.openf1_base_url == "https://api.openf1.org/v1"
    assert settings.openf1_rate_limit_rps == 3.0
    assert settings.openf1_timeout_connect == 5.0
    assert settings.openf1_timeout_read == 30.0
    assert settings.openf1_max_retries == 5
    assert settings.data_output_dir == Path("data/processed")
    assert settings.log_level == "INFO"


def test_settings_custom_values() -> None:
    """Valida se parâmetros customizados sobrescrevem corretamente os padrões."""
    # Arrange & Act
    settings = Settings(
        openf1_base_url="https://custom.api.org",
        openf1_rate_limit_rps=2.5,
        openf1_timeout_connect=10.0,
        openf1_timeout_read=60.0,
        data_output_dir=Path("custom/data"),
    )

    # Assert
    assert settings.openf1_base_url == "https://custom.api.org"
    assert settings.openf1_rate_limit_rps == 2.5
    assert settings.data_output_dir == Path("custom/data")


def test_get_settings_lru_cache() -> None:
    """Valida se get_settings() utiliza cache singleton de forma determinística."""
    # Arrange & Act
    s1 = get_settings()
    s2 = get_settings()

    # Assert
    assert s1 is s2
