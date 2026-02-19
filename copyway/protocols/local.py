import shutil
from pathlib import Path
from .base import Protocol
from ..exceptions import ProtocolError
from ..utils.logger import logger
from ..utils.validators import (
    validate_source,
    validate_destination,
    validate_disk_space,
)
from ..utils.progress import get_file_size, ProgressCallback


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
            show_progress = options.get("progress", True)

            logger.info(f"Copiando {source} -> {destination}")

            if show_progress:
                total_size = get_file_size(source)
                progress = ProgressCallback(total_size, "Copiando")

            if src.is_file():
                if preserve_metadata:
                    shutil.copy2(source, destination, follow_symlinks=follow_symlinks)
                else:
                    shutil.copy(source, destination, follow_symlinks=follow_symlinks)

                if show_progress:
                    progress.update(total_size, Path(source).name)
                    progress.finish()
            else:

                def copy_with_progress(src, dst, *args, **kwargs):
                    shutil.copy2(src, dst, *args, **kwargs)
                    if show_progress:
                        file_size = Path(src).stat().st_size
                        progress.update(file_size, Path(src).name)

                shutil.copytree(
                    source,
                    destination,
                    symlinks=not follow_symlinks,
                    dirs_exist_ok=True,
                    copy_function=copy_with_progress,
                )

                if show_progress:
                    progress.finish()

            logger.info("Copia completada exitosamente")
        except Exception as e:
            logger.error(f"Error en copia local: {e}")
            raise ProtocolError(f"Error en copia local: {e}")
