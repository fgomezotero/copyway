"""Excepciones personalizadas para CopyWay.

Este módulo define la jerarquía de excepciones utilizadas en toda la aplicación.
Todas las excepciones heredan de CopyWayError para facilitar el manejo centralizado.
"""


class CopyWayError(Exception):
    """Excepción base para todas las excepciones de CopyWay.

    Todas las excepciones específicas del proyecto deben heredar de esta clase
    para permitir un manejo de errores consistente.
    """

    pass


class ProtocolError(CopyWayError):
    """Error durante operaciones de protocolo.

    Se lanza cuando ocurre un error durante la ejecución de operaciones
    de copia o validación en cualquier protocolo (local, SSH, SFTP, HDFS).
    """

    pass


class ValidationError(CopyWayError):
    """Error de validación de entrada.

    Se lanza cuando fallan las validaciones de source, destination,
    permisos, espacio en disco o conectividad.
    """

    pass


class ConfigError(CopyWayError):
    """Error de configuración.

    Se lanza cuando hay problemas al cargar o parsear el archivo
    de configuración YAML.
    """

    pass
