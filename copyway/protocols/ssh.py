import subprocess
from .base import Protocol
from ..exceptions import ProtocolError
from ..utils.logger import logger


class SSHProtocol(Protocol):
    def validate(self, source, destination):
        from ..utils.validators import validate_source, validate_destination
        validate_source(source, "ssh")
        validate_destination(destination, "ssh")
        return True

    def copy(self, source, destination, **options):
        try:
            port = options.get("port", self.config.get("port", 22))
            user = options.get("user", self.config.get("user"))
            key_file = options.get("key_file", self.config.get("key_file"))
            compress = options.get("compress", self.config.get("compress", False))
            
            cmd = ["scp", "-r"]
            
            if port != 22:
                cmd.extend(["-P", str(port)])
            if key_file:
                cmd.extend(["-i", key_file])
            if compress:
                cmd.append("-C")
            
            cmd.extend([source, destination])
            
            logger.info(f"Ejecutando: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info("Copia SSH completada exitosamente")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error en copia SSH: {e.stderr}")
            raise ProtocolError(f"Error en copia SSH: {e.stderr}")
        except Exception as e:
            logger.error(f"Error en copia SSH: {e}")
            raise ProtocolError(f"Error en copia SSH: {e}")
