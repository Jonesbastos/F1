"""Ponto de entrada CLI principal da plataforma de dados da Fórmula 1."""

import os

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import argparse
import sys
from collections.abc import Sequence

from f1.config.settings import get_settings
from f1.pipelines.historical_pipeline import HistoricalPipeline
from f1.pipelines.session_pipeline import SessionPipeline
from f1.utils.exceptions import F1PlatformError
from f1.utils.logger import get_logger

logger = get_logger("f1.main")


def parse_arguments(args: Sequence[str] | None = None) -> argparse.Namespace:
    """Interpreta os argumentos de linha de comando da CLI.

    Args:
        args: Argumentos customizados ou None para ler sys.argv.

    Returns:
        Namespace com os argumentos parseados.
    """
    parser = argparse.ArgumentParser(
        description="F1 Data Platform — Ingestão e Processamento OpenF1",
    )

    parser.add_argument(
        "--session-key",
        type=str,
        default=None,
        help="ID da sessão específica para processar (ou 'latest').",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=None,
        help="Temporada para extração histórica em lote (ex: 2024).",
    )
    parser.add_argument(
        "--country",
        type=str,
        default=None,
        help="Filtro de país para extração histórica (ex: Brazil).",
    )
    parser.add_argument(
        "--include-telemetry",
        action="store_true",
        help="Habilita a extração de telemetria veicular e coordenadas 3D.",
    )
    parser.add_argument(
        "--telemetry-driver",
        type=int,
        default=None,
        help="Número do piloto para filtrar na telemetria veicular.",
    )

    return parser.parse_args(args)


def main(argv: Sequence[str] | None = None) -> int:
    """Função orquestradora da interface de comando.

    Args:
        argv: Lista opcional de argumentos de execução.

    Returns:
        Código de status do processo (0 para sucesso, 1 para falha).
    """
    args = parse_arguments(argv)
    settings = get_settings()
    logger.info("Iniciando F1 Data Platform com configurações: %s", settings.openf1_base_url)

    try:
        if args.year is not None:
            pipeline = HistoricalPipeline()
            result = pipeline.run(
                year=args.year,
                country_name=args.country,
                include_telemetry=args.include_telemetry,
            )
            logger.info("Execução histórica finalizada: %s", result)
        else:
            session_key = args.session_key or "latest"
            session_pipe = SessionPipeline()
            result = session_pipe.run(
                session_key=session_key,
                include_telemetry=args.include_telemetry,
                telemetry_driver=args.telemetry_driver,
            )
            logger.info("Execução de sessão finalizada: %s", result)

        return 0

    except F1PlatformError as exc:
        logger.error("Erro da plataforma F1 durante execução: %s", exc, exc_info=True)
        return 1
    except Exception as exc:
        logger.critical("Erro inesperado durante execução da CLI: %s", exc, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
