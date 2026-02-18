import subprocess
from .base import Protocol
from ..exceptions import ProtocolError
from ..utils.logger import logger


class HDFSProtocol(Protocol):
    def validate(self, source, destination):
        from ..utils.validators import validate_source, validate_destination
        validate_source(source, "hdfs")
        validate_destination(destination, "hdfs")
        return True

    def copy(self, source, destination, **options):
        try:
            # Detectar dirección: si source empieza con / y no existe localmente, es HDFS
            is_hdfs_source = self._is_hdfs_path(source)
            is_hdfs_dest = self._is_hdfs_path(destination)
            
            if is_hdfs_source and not is_hdfs_dest:
                # Descargar desde HDFS a local
                self._download_from_hdfs(source, destination, **options)
            elif not is_hdfs_source and is_hdfs_dest:
                # Subir desde local a HDFS
                self._upload_to_hdfs(source, destination, **options)
            else:
                raise ProtocolError("Debe especificar una ruta HDFS y una local")
            
            logger.info("Copia HDFS completada exitosamente")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error en copia HDFS: {e.stderr}")
            raise ProtocolError(f"Error en copia HDFS: {e.stderr}")
        except Exception as e:
            logger.error(f"Error en copia HDFS: {e}")
            raise ProtocolError(f"Error en copia HDFS: {e}")
    
    def _is_hdfs_path(self, path):
        """Detecta si una ruta es HDFS (empieza con / o hdfs://)"""
        import os
        if path.startswith("hdfs://"):
            return True
        if path.startswith("/") and not os.path.exists(path):
            return True
        return False
    
    def _upload_to_hdfs(self, source, destination, **options):
        """Subir archivo/directorio desde local a HDFS"""
        replication = options.get("replication", self.config.get("replication"))
        overwrite = options.get("overwrite", self.config.get("overwrite", False))
        permission = options.get("permission", self.config.get("permission"))
        
        cmd = ["hdfs", "dfs", "-put"]
        
        if overwrite:
            cmd.append("-f")
        
        cmd.extend([source, destination])
        
        logger.info(f"Subiendo a HDFS: {' '.join(cmd)}")
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        if replication:
            subprocess.run(["hdfs", "dfs", "-setrep", str(replication), destination], check=True)
        
        if permission:
            subprocess.run(["hdfs", "dfs", "-chmod", permission, destination], check=True)
    
    def _download_from_hdfs(self, source, destination, **options):
        """Descargar archivo/directorio desde HDFS a local"""
        overwrite = options.get("overwrite", self.config.get("overwrite", False))
        
        cmd = ["hdfs", "dfs", "-get"]
        
        if overwrite:
            cmd.append("-f")
        
        cmd.extend([source, destination])
        
        logger.info(f"Descargando desde HDFS: {' '.join(cmd)}")
        subprocess.run(cmd, check=True, capture_output=True, text=True)
