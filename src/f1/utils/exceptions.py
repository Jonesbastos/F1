"""Hierarquia de exceções customizadas da plataforma F1."""


class F1PlatformError(Exception):
    """Exceção base para todos os erros da plataforma F1."""


class OpenF1APIError(F1PlatformError):
    """Exceção lançada quando ocorre erro de comunicação ou resposta inválida da OpenF1 API."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        """Inicializa o erro da API OpenF1 com mensagem e código HTTP opcional.

        Args:
            message: Descrição da falha.
            status_code: Código de status HTTP retornado, se aplicável.
        """
        super().__init__(message)
        self.status_code = status_code


class RateLimitExceededError(OpenF1APIError):
    """Exceção lançada quando o limite de requisições por segundo é violado ou HTTP 429."""


class TransformationError(F1PlatformError):
    """Exceção lançada quando falha a limpeza, validação ou transformação dos dados."""


class StorageError(F1PlatformError):
    """Exceção lançada quando ocorre erro na escrita ou persistência no Data Lake."""


class DataValidationError(F1PlatformError):
    """Exceção lançada quando os dados violam o contrato de integridade de esquema."""
