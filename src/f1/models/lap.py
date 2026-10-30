"""Modelos Pydantic para voltas e tempos de setor."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Lap(BaseModel):
    """Representa o registro de uma volta cronometrada na sessão.

    Attributes:
        lap_number: Número sequencial da volta.
        session_key: ID da sessão em que a volta ocorreu.
        meeting_key: ID do evento associado.
        driver_number: Número do carro do piloto.
        lap_duration: Tempo total da volta em segundos.
        duration_sector_1: Duração registrada no 1º setor da pista em segundos.
        duration_sector_2: Duração registrada no 2º setor da pista em segundos.
        duration_sector_3: Duração registrada no 3º setor da pista em segundos.
        segments_sector_1: Status de mini-setores do setor 1.
        segments_sector_2: Status de mini-setores do setor 2.
        segments_sector_3: Status de mini-setores do setor 3.
        is_pit_out_lap: Indica se foi uma volta de saída do pit lane.
        date_start: Timestamp de início da volta em UTC.
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    lap_number: int = Field(..., description="Número da volta")
    session_key: int = Field(..., description="ID da sessão")
    driver_number: int = Field(..., description="Número do piloto")
    meeting_key: int | None = Field(default=None, description="ID do evento")
    lap_duration: float | None = Field(default=None, description="Tempo da volta em segundos")
    duration_sector_1: float | None = Field(default=None, description="Tempo do setor 1")
    duration_sector_2: float | None = Field(default=None, description="Tempo do setor 2")
    duration_sector_3: float | None = Field(default=None, description="Tempo do setor 3")
    segments_sector_1: list[int | float | None] | None = Field(
        default=None, description="Segmentos do setor 1"
    )
    segments_sector_2: list[int | float | None] | None = Field(
        default=None, description="Segmentos do setor 2"
    )
    segments_sector_3: list[int | float | None] | None = Field(
        default=None, description="Segmentos do setor 3"
    )
    is_pit_out_lap: bool | None = Field(default=None, description="Volta de saída dos boxes")
    date_start: datetime | None = Field(default=None, description="Data/hora de início da volta")
