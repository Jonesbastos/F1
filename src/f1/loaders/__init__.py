"""Submódulo de loaders e persistência colunar."""

from f1.loaders.base import BaseLoader
from f1.loaders.parquet_loader import ParquetLoader

__all__ = ["BaseLoader", "ParquetLoader"]
