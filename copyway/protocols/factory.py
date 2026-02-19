"""Factory para crear instancias de protocolos de transferencia.

Este módulo implementa el patrón Factory para gestionar el registro
y creación de protocolos de transferencia.
"""

from ..exceptions import ProtocolError
from ..utils.logger import logger


class ProtocolFactory:
    """Factory para crear y gestionar protocolos de transferencia.
    
    Implementa el patrón Factory para registrar y crear instancias de
    protocolos. Soporta protocolos built-in y personalizados.
    
    Attributes:
        _protocols (dict): Registro de protocolos disponibles
    
    Example:
        >>> from copyway.protocols import ProtocolFactory
        >>> protocol = ProtocolFactory.create('local', {'preserve_metadata': True})
        >>> protocol.copy('/origen', '/destino')
    """
    
    _protocols = {}

    @classmethod
    def register(cls, name, protocol_class):
        """Registra un nuevo protocolo.
        
        Args:
            name (str): Nombre del protocolo (ej: 'local', 'ssh', 'sftp')
            protocol_class (type): Clase del protocolo que hereda de Protocol
        
        Example:
            >>> class S3Protocol(Protocol):
            ...     pass
            >>> ProtocolFactory.register('s3', S3Protocol)
        """
        cls._protocols[name] = protocol_class
        logger.debug(f"Protocolo registrado: {name}")

    @classmethod
    def create(cls, name, config=None):
        """Crea una instancia de protocolo.
        
        Args:
            name (str): Nombre del protocolo registrado
            config (dict, optional): Configuración del protocolo
        
        Returns:
            Protocol: Instancia del protocolo solicitado
        
        Raises:
            ProtocolError: Si el protocolo no está registrado
        
        Example:
            >>> protocol = ProtocolFactory.create('sftp', {'port': 22})
        """
        if name not in cls._protocols:
            raise ProtocolError(f"Protocolo no soportado: {name}")
        return cls._protocols[name](config)

    @classmethod
    def list_protocols(cls):
        """Lista todos los protocolos registrados.
        
        Returns:
            list: Lista de nombres de protocolos disponibles
        
        Example:
            >>> protocols = ProtocolFactory.list_protocols()
            >>> print(protocols)
            ['local', 'ssh', 'sftp', 'hdfs']
        """
        return list(cls._protocols.keys())


# Registro de protocolos built-in
from .local import LocalProtocol
from .ssh import SSHProtocol
from .hdfs import HDFSProtocol
from .sftp import SFTPProtocol

ProtocolFactory.register("local", LocalProtocol)
ProtocolFactory.register("ssh", SSHProtocol)
ProtocolFactory.register("hdfs", HDFSProtocol)
ProtocolFactory.register("sftp", SFTPProtocol)
