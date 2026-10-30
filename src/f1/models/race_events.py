"""Modelos Pydantic para eventos dinâmicos de corrida (pits, stints, posições, intervalos)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PitStop(BaseModel):
    """Representa uma passagem pelo pit lane e troca de pneus/ajustes.

    Attributes:
        session_key: Identificador da sessão.
        meeting_key: Identificador do evento pai.
        driver_number: Número de corrida do piloto.
        lap_number: Volta em que a entrada no pit foi executada.
        pit_duration: Tempo total decorrido no pit lane em segundos.
        stop_duration: Tempo em que o veículo permaneceu estático para o serviço.
        date: Timestamp do momento de entrada no pit lane.
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    session_key: int = Field(..., description="ID da sessão")
    driver_number: int = Field(..., description="Número do piloto")
    lap_number: int = Field(..., description="Volta do pit stop")
    meeting_key: int | None = Field(default=None, description="ID do evento")
    pit_duration: float | None = Field(default=None, description="Duração total no pit lane")
    stop_duration: float | None = Field(default=None, description="Tempo parado no box")
    date: datetime | None = Field(default=None, description="Data/hora do pit stop")


class Stint(BaseModel):
    """Representa um turno de corrida contínuo com um jogo de pneus específico.

    Attributes:
        session_key: Identificador da sessão.
        meeting_key: Identificador do evento pai.
        driver_number: Número de corrida do piloto.
        stint_number: Número sequencial do stint no GP.
        compound: Tipo de composto de pneus (SOFT, MEDIUM, HARD, INTERMEDIATE, WET).
        tyre_age_at_start: Voltas prévias acumuladas pelo composto.
        lap_start: Volta da sessão onde o stint iniciou.
        lap_end: Volta da sessão onde o stint encerrou.
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    session_key: int = Field(..., description="ID da sessão")
    driver_number: int = Field(..., description="Número do piloto")
    stint_number: int = Field(..., description="Número ordinal do stint")
    meeting_key: int | None = Field(default=None, description="ID do evento")
    compound: str | None = Field(default=None, description="Composto de pneu")
    tyre_age_at_start: int | None = Field(default=None, description="Idade inicial do pneu")
    lap_start: int | None = Field(default=None, description="Volta de início do stint")
    lap_end: int | None = Field(default=None, description="Volta final do stint")


class Position(BaseModel):
    """Representa o posicionamento do piloto na corrida em determinado instante.

    Attributes:
        session_key: Identificador da sessão.
        meeting_key: Identificador do evento pai.
        driver_number: Número de corrida do piloto.
        position: Posição numérica corrente (1 = líder).
        date: Timestamp da atualização da posição.
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    session_key: int = Field(..., description="ID da sessão")
    driver_number: int = Field(..., description="Número do piloto")
    position: int = Field(..., description="Classificação instantânea")
    meeting_key: int | None = Field(default=None, description="ID do evento")
    date: datetime | None = Field(default=None, description="Timestamp da posição")


class Interval(BaseModel):
    """Representa o gap temporal de corrida entre concorrentes.

    Attributes:
        session_key: Identificador da sessão.
        meeting_key: Identificador do evento pai.
        driver_number: Número de corrida do piloto.
        gap_to_leader: Diferença de tempo para o líder (segundos ou string de voltas atrasadas).
        interval: Diferença de tempo para o carro imediatamente anterior.
        date: Timestamp do cálculo do intervalo.
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    session_key: int = Field(..., description="ID da sessão")
    driver_number: int = Field(..., description="Número do piloto")
    meeting_key: int | None = Field(default=None, description="ID do evento")
    gap_to_leader: float | str | None = Field(default=None, description="Gap para o líder")
    interval: float | str | None = Field(
        default=None, description="Intervalo para o carro à frente"
    )
    date: datetime | None = Field(default=None, description="Timestamp do intervalo")
