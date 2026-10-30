"""Gravador colunar em formato Apache Parquet com suporte a particionamento."""

from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from f1.config.settings import Settings, get_settings
from f1.loaders.base import BaseLoader
from f1.utils.exceptions import StorageError
from f1.utils.logger import get_logger

logger = get_logger("f1.loaders.parquet")


class ParquetLoader(BaseLoader):
    """Persiste DataFrames em arquivos colunares Parquet com particionamento idempotente.

    Attributes:
        base_dir: Diretório raiz do Data Lake analítico.
    """

    def __init__(
        self, base_dir: Path | str | None = None, settings: Settings | None = None
    ) -> None:
        """Inicializa o carregador Parquet.

        Args:
            base_dir: Caminho base para escrita. Se omitido, usa DATA_OUTPUT_DIR dos settings.
            settings: Instância de configurações.
        """
        cfg = settings or get_settings()
        self.base_dir = Path(base_dir) if base_dir is not None else cfg.data_output_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def write(
        self,
        df: pd.DataFrame,
        table_name: str,
        partition_cols: list[str] | None = None,
    ) -> Path:
        """Grava o DataFrame em formato Parquet com compressão snappy.

        Caso partition_cols seja fornecido, o dataset será particionado no estilo Hive
        (ex: `table_name/col1=val1/col2=val2/...`).

        Args:
            df: DataFrame a ser persistido.
            table_name: Nome do diretório/tabela (ex: 'meetings', 'laps').
            partition_cols: Lista opcional de colunas para particionamento.

        Returns:
            Path apontando para o diretório ou arquivo persistido.

        Raises:
            StorageError: Se ocorrer falha durante a serialização ou gravação em disco.
        """
        if df.empty:
            logger.warning(
                "DataFrame vazio fornecido para tabela %s. Operação ignorada.", table_name
            )
            target_dir = self.base_dir / table_name
            target_dir.mkdir(parents=True, exist_ok=True)
            return target_dir

        target_dir = self.base_dir / table_name
        target_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Converte para PyArrow Table
            table = pa.Table.from_pandas(df, preserve_index=False)

            if partition_cols:
                # Verifica se todas as colunas de partição estão presentes
                missing_cols = [c for c in partition_cols if c not in df.columns]
                if missing_cols:
                    raise ValueError(f"Colunas de partição ausentes no DataFrame: {missing_cols}")

                pq.write_to_dataset(
                    table,
                    root_path=str(target_dir),
                    partition_cols=partition_cols,
                    compression="snappy",
                    existing_data_behavior="delete_matching",
                )
                logger.info(
                    "Tabela particionada '%s' gravada com sucesso em %s (%d linhas, partições=%s)",
                    table_name,
                    target_dir,
                    len(df),
                    partition_cols,
                )
            else:
                output_file = target_dir / f"{table_name}.parquet"
                pq.write_table(table, output_file, compression="snappy")
                logger.info(
                    "Tabela '%s' gravada com sucesso em %s (%d linhas)",
                    table_name,
                    output_file,
                    len(df),
                )
                return output_file

            return target_dir
        except Exception as exc:
            msg = f"Falha ao persistir tabela {table_name} em Parquet: {exc}"
            logger.error(msg)
            raise StorageError(msg) from exc
