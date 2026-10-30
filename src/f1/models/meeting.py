"""Modelos Pydantic para Grandes Prêmios e Sessões da Fórmula 1."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Meeting(BaseModel):
    """Representa um fim de semana de Grande Prêmio ou teste oficial.

    Attributes:
        meeting_key: Identificador único do evento.
        meeting_name: Nome oficial do evento (ex: São Paulo Grand Prix).
        meeting_code: Código abreviado do evento (ex: BRA).
        year: Temporada correspondente ao evento.
        circuit_key: Identificador do circuito.
        circuit_short_name: Nome popular do circuito (ex: Interlagos).
        country_name: Nome do país anfitrião.
        country_code: Código ISO de 3 letras do país.
        date_start: Data e hora de início do evento em UTC.
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    meeting_key: int = Field(..., description="ID único do GP")
    meeting_name: str = Field(..., description="Nome oficial do GP")
    meeting_code: str | None = Field(default=None, description="Código do evento")
    year: int = Field(..., description="Ano da temporada")
    circuit_key: int | None = Field(default=None, description="ID do circuito")
    circuit_short_name: str | None = Field(default=None, description="Nome do circuito")
    country_name: str | None = Field(default=None, description="País do evento")
    country_code: str | None = Field(default=None, description="Código ISO do país")
    date_start: datetime | None = Field(default=None, description="Início do evento")


class Session(BaseModel):
    """Representa uma sessão de pista específica (Treino, Classificação, Sprint, Corrida).

    Attributes:
        session_key: Identificador único da sessão.
        session_name: Nome descritivo da sessão (ex: Race, Practice 1).
        session_type: Tipo da sessão (Practice, Qualifying, Race, Sprint).
        meeting_key: Identificador do evento pai.
        year: Ano da temporada.
        date_start: Data e hora de abertura da sessão em UTC.
        date_end: Data e hora de encerramento da sessão em UTC.
        gmt_offset: Diferença de fuso horário local.
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    session_key: int = Field(..., description="ID único da sessão")
    session_name: str = Field(..., description="Nome da sessão")
    session_type: str | None = Field(default=None, description="Tipo de sessão")
    meeting_key: int = Field(..., description="ID do evento associado")
    year: int | None = Field(default=None, description="Ano da temporada")
    date_start: datetime | None = Field(default=None, description="Início da sessão")
    date_end: datetime | None = Field(default=None, description="Fim da sessão")
    gmt_offset: str | None = Field(default=None, description="Offset GMT da sessão")
