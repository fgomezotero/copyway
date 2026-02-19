"""Clase base abstracta para protocolos de transferencia.

Este módulo define la interfaz que deben implementar todos los protocolos
de transferencia en CopyWay.
"""

from abc import ABC, abstractmethod


class Protocol(ABC):
    """Clase base abstracta para protocolos de transferencia.

    Todos los protocolos (local, SSH, SFTP, HDFS) deben heredar de esta clase
    e implementar los métodos abstractos copy() y validate().

    Attributes:
        config (dict): Configuración específica del protocolo

    Example:
        >>> class CustomProtocol(Protocol):
        ...     def validate(self, source, destination, **options):
        ...         return True
        ...     def copy(self, source, destination, **options):
        ...         # Implementación de copia
        ...         pass
    """

    def __init__(self, config=None):
        """Inicializa el protocolo con configuración opcional.

        Args:
            config (dict, optional): Configuración del protocolo. Default: {}
        """
        self.config = config or {}

    @abstractmethod
    def copy(self, source, destination, **options):
        """Copia archivos/directorios de origen a destino.

        Args:
            source (str): Ruta de origen
            destination (str): Ruta de destino
            **options: Opciones específicas del protocolo

        Raises:
            ProtocolError: Si ocurre un error durante la copia
        """
        pass

    @abstractmethod
    def validate(self, source, destination, **options):
        """Valida que la operación de copia es posible.

        Verifica permisos, conectividad, espacio en disco, etc.

        Args:
            source (str): Ruta de origen
            destination (str): Ruta de destino
            **options: Opciones específicas del protocolo

        Returns:
            bool: True si la validación es exitosa

        Raises:
            ValidationError: Si la validación falla
        """
        pass
