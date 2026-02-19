"""Configuración de logging para CopyWay.

Este módulo proporciona funciones para configurar el sistema de logging
de la aplicación con formato consistente.
"""

import logging
import sys


def setup_logger(name="copyway", level=logging.INFO):
    """Configura y retorna un logger para la aplicación.

    Crea un logger con handler de consola y formato estandarizado.
    Previene la creación de múltiples handlers verificando si ya existen.

    Args:
        name (str): Nombre del logger. Default: "copyway"
        level (int): Nivel de logging. Default: logging.INFO

    Returns:
        logging.Logger: Logger configurado

    Example:
        >>> logger = setup_logger(level=logging.DEBUG)
        >>> logger.info("Mensaje de información")
        >>> logger.debug("Mensaje de debug")
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(handler)

    return logger


# Logger global de la aplicación
logger = setup_logger()
