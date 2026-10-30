"""Interface base para componentes de carga e persistência de dados."""

from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd


class BaseLoader(ABC):
    """Interface abstrata para persistência de conjuntos de dados."""

    @abstractmethod
    def write(
        self,
        df: pd.DataFrame,
        table_name: str,
        partition_cols: list[str] | None = None,
    ) -> Path:
        """Persiste um DataFrame no destino configurado.

        Args:
            df: Conjunto de dados tabular a ser persistido.
            table_name: Nome da entidade ou tabela de destino.
            partition_cols: Lista de colunas utilizadas para particionamento.

        Returns:
            Caminho do diretório ou arquivo persistido.
        """
