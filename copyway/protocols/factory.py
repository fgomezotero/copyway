from ..exceptions import ProtocolError
from ..utils.logger import logger


class ProtocolFactory:
    _protocols = {}

    @classmethod
    def register(cls, name, protocol_class):
        cls._protocols[name] = protocol_class
        logger.debug(f"Protocolo registrado: {name}")

    @classmethod
    def create(cls, name, config=None):
        if name not in cls._protocols:
            raise ProtocolError(f"Protocolo no soportado: {name}")
        return cls._protocols[name](config)

    @classmethod
    def list_protocols(cls):
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
