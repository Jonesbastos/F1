"""Modelos Pydantic para telemetria de alta frequência e posição do carro."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CarData(BaseModel):
    """Representa uma amostra instantânea de telemetria dos sensores do carro.

    Attributes:
        session_key: Identificador da sessão.
        meeting_key: Identificador do evento pai.
        driver_number: Número de corrida do piloto.
        speed: Velocidade instantânea aferida em km/h.
        rpm: Rotações por minuto do motor de combustão interna.
        gear: Marcha engrenada no instante (0 para neutro).
        throttle: Porcentagem de curso do pedal acelerador (0 a 100%).
        brake: Indicador ou pressão de acionamento do freio.
        drs: Status do acionamento da asa móvel (DRS).
        date: Timestamp exato da leitura do sensor em UTC.
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    session_key: int = Field(..., description="ID da sessão")
    driver_number: int = Field(..., description="Número do piloto")
    date: datetime = Field(..., description="Data/hora da amostra em UTC")
    meeting_key: int | None = Field(default=None, description="ID do GP")
    speed: int | None = Field(default=None, description="Velocidade em km/h")
    rpm: int | None = Field(default=None, description="Rotações por minuto")
    gear: int | None = Field(default=None, description="Marcha engatada")
    throttle: int | None = Field(default=None, description="Acelerador em %")
    brake: int | None = Field(default=None, description="Freio acionado")
    drs: int | None = Field(default=None, description="Status do DRS")


class Location(BaseModel):
    """Representa as coordenadas espaciais 3D instantâneas do carro no circuito.

    Attributes:
        session_key: Identificador da sessão.
        meeting_key: Identificador do evento pai.
        driver_number: Número de corrida do piloto.
        x: Coordenada cartesiana longitudinal do traçado.
        y: Coordenada cartesiana transversal do traçado.
        z: Coordenada de elevação/altura da pista.
        date: Timestamp exato da leitura em UTC.
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    session_key: int = Field(..., description="ID da sessão")
    driver_number: int = Field(..., description="Número do piloto")
    date: datetime = Field(..., description="Data/hora da coordenada em UTC")
    meeting_key: int | None = Field(default=None, description="ID do GP")
    x: float | None = Field(default=None, description="Coordenada X")
    y: float | None = Field(default=None, description="Coordenada Y")
    z: float | None = Field(default=None, description="Coordenada Z de altitude")
