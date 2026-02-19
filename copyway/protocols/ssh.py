import subprocess
from pathlib import Path
from .base import Protocol
from ..exceptions import ProtocolError
from ..utils.logger import logger
from ..utils.progress import get_file_size, format_size, format_speed
import time


class SSHProtocol(Protocol):
    def validate(self, source, destination):
        from ..utils.validators import validate_source, validate_destination

        validate_source(source, "ssh")
        validate_destination(destination, "ssh")
        return True

    def copy(self, source, destination, **options):
        try:
            port = options.get("port", self.config.get("port", 22))
            key_file = options.get("key_file", self.config.get("key_file"))
            compress = options.get("compress", self.config.get("compress", False))
            show_progress = options.get("progress", True)

            # Obtener tamaño si es local
            total_size = 0
            if Path(source).exists():
                total_size = get_file_size(source)

            cmd = ["scp", "-r"]

            if port != 22:
                cmd.extend(["-P", str(port)])
            if key_file:
                cmd.extend(["-i", key_file])
            if compress:
                cmd.append("-C")

            cmd.extend([source, destination])

            logger.info(f"Ejecutando: {' '.join(cmd)}")

            if show_progress and total_size > 0:
                print(f"Copiando {format_size(total_size)}...", flush=True)
                start_time = time.time()

            subprocess.run(cmd, check=True, capture_output=True, text=True)

            if show_progress and total_size > 0:
                elapsed = time.time() - start_time
                speed = total_size / elapsed if elapsed > 0 else 0
                print(
                    f"✓ Completado: {format_size(total_size)} en {elapsed:.1f}s ({format_speed(speed)})"
                )

            logger.info("Copia SSH completada exitosamente")

        except subprocess.CalledProcessError as e:
            logger.error(f"Error en copia SSH: {e.stderr}")
            raise ProtocolError(f"Error en copia SSH: {e.stderr}")
        except Exception as e:
            logger.error(f"Error en copia SSH: {e}")
            raise ProtocolError(f"Error en copia SSH: {e}")
