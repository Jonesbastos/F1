"""Testes unitários para persistência de dados em Parquet."""

from pathlib import Path

import pandas as pd
import pytest

from f1.loaders.parquet_loader import ParquetLoader
from f1.utils.exceptions import StorageError


def test_parquet_loader_write_unpartitioned(tmp_path: Path) -> None:
    """Verifica gravação de tabela Parquet direta sem particionamento."""
    # Arrange
    loader = ParquetLoader(base_dir=tmp_path)
    df = pd.DataFrame([{"id": 1, "name": "Monza"}, {"id": 2, "name": "Spa"}])

    # Act
    output_path = loader.write(df, "circuits")

    # Assert
    assert output_path.exists()
    df_read = pd.read_parquet(output_path)
    assert len(df_read) == 2
    assert "name" in df_read.columns


def test_parquet_loader_write_partitioned(tmp_path: Path) -> None:
    """Verifica gravação de tabela Parquet com particionamento no formato Hive."""
    # Arrange
    loader = ParquetLoader(base_dir=tmp_path)
    df = pd.DataFrame(
        [
            {"year": 2024, "round": 1, "name": "Bahrain"},
            {"year": 2024, "round": 2, "name": "Jeddah"},
            {"year": 2023, "round": 1, "name": "Bahrain"},
        ]
    )

    # Act
    output_dir = loader.write(df, "races", partition_cols=["year"])

    # Assert
    assert output_dir.exists()
    assert (output_dir / "year=2024").exists()
    assert (output_dir / "year=2023").exists()
    df_read = pd.read_parquet(output_dir)
    assert len(df_read) == 3


def test_parquet_loader_write_empty(tmp_path: Path) -> None:
    """Verifica comportamento defensivo ao receber DataFrame vazio."""
    # Arrange
    loader = ParquetLoader(base_dir=tmp_path)
    df_empty = pd.DataFrame()

    # Act
    output = loader.write(df_empty, "empty_table")

    # Assert
    assert output.exists()


def test_parquet_loader_missing_partition_column(tmp_path: Path) -> None:
    """Verifica lançamento de StorageError caso a partição não conste no DataFrame."""
    # Arrange
    loader = ParquetLoader(base_dir=tmp_path)
    df = pd.DataFrame([{"driver": "VER"}])

    # Act & Assert
    with pytest.raises(StorageError):
        loader.write(df, "invalid", partition_cols=["non_existing_col"])
