import shutil
from pathlib import Path
from .base import Protocol
from ..exceptions import ProtocolError
from ..utils.logger import logger
from ..utils.validators import validate_source, validate_destination, validate_disk_space


class LocalProtocol(Protocol):
    def validate(self, source, destination):
        validate_source(source, "local")
        validate_destination(destination, "local")
        validate_disk_space(source, destination, "local")

    def copy(self, source, destination, **options):
        try:
            src = Path(source)
            preserve_metadata = options.get("preserve_metadata", True)
            follow_symlinks = options.get("follow_symlinks", False)
            
            logger.info(f"Copiando {source} -> {destination}")
            
            if src.is_file():
                if preserve_metadata:
                    shutil.copy2(source, destination, follow_symlinks=follow_symlinks)
                else:
                    shutil.copy(source, destination, follow_symlinks=follow_symlinks)
            else:
                shutil.copytree(source, destination, symlinks=not follow_symlinks, dirs_exist_ok=True)
            
            logger.info("Copia completada exitosamente")
        except Exception as e:
            logger.error(f"Error en copia local: {e}")
            raise ProtocolError(f"Error en copia local: {e}")
