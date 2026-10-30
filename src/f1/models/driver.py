"""Modelos Pydantic para pilotos e equipes de Fórmula 1."""

from pydantic import BaseModel, ConfigDict, Field


class Driver(BaseModel):
    """Representa um piloto registrado para uma sessão específica.

    Attributes:
        driver_number: Número oficial do carro do piloto.
        session_key: ID da sessão em que o piloto participou.
        meeting_key: ID do evento associado.
        broadcast_name: Nome abreviado exibido nas transmissões de TV (ex: M VERSTAPPEN).
        full_name: Nome completo do piloto.
        name_acronym: Sigla de três letras do piloto (ex: VER).
        team_name: Nome oficial da equipe/construtor.
        team_colour: Código hexadecimal da cor da equipe (sem o prefixo # na API).
        headshot_url: URL da imagem oficial do piloto.
        country_code: Código do país do piloto.
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    driver_number: int = Field(..., description="Número de corrida do piloto")
    session_key: int | None = Field(default=None, description="ID da sessão")
    meeting_key: int | None = Field(default=None, description="ID do evento")
    broadcast_name: str | None = Field(default=None, description="Nome na transmissão")
    full_name: str | None = Field(default=None, description="Nome completo")
    name_acronym: str | None = Field(default=None, description="Acrônimo do piloto")
    team_name: str | None = Field(default=None, description="Nome da escuderia")
    team_colour: str | None = Field(default=None, description="Cor hexadecimal da equipe")
    headshot_url: str | None = Field(default=None, description="URL da foto")
    country_code: str | None = Field(default=None, description="Código de país")
