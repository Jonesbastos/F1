"""Módulo de configurações e variáveis de ambiente da plataforma F1."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação validadas via variáveis de ambiente.

    Attributes:
        openf1_base_url: URL base para requisições na API OpenF1.
        openf1_rate_limit_rps: Limite máximo de requisições por segundo.
        openf1_timeout_connect: Timeout de conexão em segundos.
        openf1_timeout_read: Timeout de leitura/resposta em segundos.
        openf1_max_retries: Quantidade máxima de retentativas em falhas transitórias.
        openf1_backoff_factor: Fator multiplicador do backoff exponencial.
        data_output_dir: Diretório raiz para persistência dos arquivos Parquet.
        log_level: Nível padrão de emissão de logs.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openf1_base_url: str = Field(
        default="https://api.openf1.org/v1",
        description="URL base da API OpenF1.",
    )
    openf1_rate_limit_rps: float = Field(
        default=3.0,
        description="Limite de requisições por segundo na API OpenF1.",
        gt=0.0,
    )
    openf1_timeout_connect: float = Field(
        default=5.0,
        description="Timeout de conexão HTTP em segundos.",
        gt=0.0,
    )
    openf1_timeout_read: float = Field(
        default=30.0,
        description="Timeout de leitura HTTP em segundos.",
        gt=0.0,
    )
    openf1_max_retries: int = Field(
        default=5,
        description="Número máximo de retentativas automáticas.",
        ge=0,
    )
    openf1_backoff_factor: float = Field(
        default=0.5,
        description="Fator de recuo exponencial para retentativas.",
        ge=0.0,
    )
    data_output_dir: Path = Field(
        default=Path("data/processed"),
        description="Diretório base para armazenamento do Data Lake analítico.",
    )
    log_level: str = Field(
        default="INFO",
        description="Nível de severidade de logging.",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Retorna uma instância singleton com as configurações da aplicação.

    Returns:
        Instância validada da classe Settings.
    """
    return Settings()
