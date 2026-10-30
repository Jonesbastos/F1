"""Modelos Pydantic para meteorologia, comissários de prova e comunicação via rádio."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WeatherRecord(BaseModel):
    """Representa a leitura periódica das condições meteorológicas do autódromo.

    Attributes:
        session_key: Identificador da sessão.
        date: Timestamp exato da leitura meteorológica em UTC.
        meeting_key: Identificador do evento pai.
        air_temperature: Temperatura ambiente em graus Celsius.
        track_temperature: Temperatura da superfície da pista em graus Celsius.
        humidity: Percentual relativo de umidade do ar.
        pressure: Pressão atmosférica em milibares.
        wind_speed: Velocidade do vento em metros por segundo (m/s).
        wind_direction: Direção do vento em graus azimutais (0 a 360°).
        rainfall: Indicador binário de chuva (0 = pista seca, 1 = chuva).
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    session_key: int = Field(..., description="ID da sessão")
    date: datetime = Field(..., description="Timestamp da medição em UTC")
    meeting_key: int | None = Field(default=None, description="ID do evento")
    air_temperature: float | None = Field(default=None, description="Temperatura do ar (°C)")
    track_temperature: float | None = Field(default=None, description="Temperatura da pista (°C)")
    humidity: float | None = Field(default=None, description="Umidade relativa (%)")
    pressure: float | None = Field(default=None, description="Pressão atmosférica (mbar)")
    wind_speed: float | None = Field(default=None, description="Velocidade do vento (m/s)")
    wind_direction: int | None = Field(default=None, description="Direção do vento em graus")
    rainfall: int | None = Field(default=None, description="Indicador de chuva (0 ou 1)")


class RaceControlMessage(BaseModel):
    """Representa uma notificação oficial emitida pela direção de prova da FIA.

    Attributes:
        session_key: Identificador da sessão.
        date: Timestamp em que a instrução foi promulgada em UTC.
        message: Texto integral descritivo da instrução.
        meeting_key: Identificador do evento pai.
        category: Categoria temática (Flag, SafetyCar, Drs, Investigation).
        flag: Cor ou status de bandeira associada (GREEN, YELLOW, RED, CHEQUERED).
        scope: Escopo da mensagem (Track, Sector, Driver).
        lap: Volta em que o evento ocorreu.
        driver_number: Número de carro do piloto advertido ou investigado.
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    session_key: int = Field(..., description="ID da sessão")
    date: datetime = Field(..., description="Timestamp da emissão")
    message: str = Field(..., description="Mensagem oficial da direção")
    meeting_key: int | None = Field(default=None, description="ID do evento")
    category: str | None = Field(default=None, description="Categoria do alerta")
    flag: str | None = Field(default=None, description="Status da bandeira")
    scope: str | None = Field(default=None, description="Escopo do alerta")
    lap: int | None = Field(default=None, description="Volta do evento")
    driver_number: int | None = Field(default=None, description="Piloto implicado")


class TeamRadioRecord(BaseModel):
    """Representa a captura de um diálogo entre engenheiro de pista e piloto.

    Attributes:
        session_key: Identificador da sessão.
        driver_number: Número de corrida do piloto comunicante.
        date: Timestamp em que o áudio foi transmitido em UTC.
        meeting_key: Identificador do evento pai.
        recording_url: URL pública do arquivo de áudio (formato MP3).
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    session_key: int = Field(..., description="ID da sessão")
    driver_number: int = Field(..., description="Número do piloto")
    date: datetime = Field(..., description="Timestamp da transmissão")
    meeting_key: int | None = Field(default=None, description="ID do evento")
    recording_url: str | None = Field(default=None, description="URL do áudio gravado")
