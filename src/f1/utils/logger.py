"""Módulo de configuração de logging estruturado da plataforma F1."""

import logging
import sys


def get_logger(name: str = "f1", level: str = "INFO") -> logging.Logger:
    """Configura e retorna uma instância do logger padrão da aplicação.

    Args:
        name: Identificador do módulo requisitante.
        level: Nível de severidade do log (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Returns:
        Logger configurado com formato estruturado e saída padronizada.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    try:
        log_level = getattr(logging, level.upper())
    except (AttributeError, TypeError):
        log_level = logging.INFO

    logger.setLevel(log_level)
    return logger
