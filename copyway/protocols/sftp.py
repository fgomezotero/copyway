import os
from pathlib import Path
from .base import Protocol
from ..exceptions import ProtocolError
from ..utils.logger import logger
from ..utils.progress import format_size, format_speed
import time

try:
    import paramiko
except ImportError:
    paramiko = None


class SFTPProtocol(Protocol):
    def validate(self, source, destination):
        if paramiko is None:
            raise ProtocolError("paramiko no instalado. Ejecutar: pip install paramiko")
        
        from ..utils.validators import validate_source, validate_destination
        validate_source(source, "sftp")
        validate_destination(destination, "sftp")
        return True

    def copy(self, source, destination, **options):
        if paramiko is None:
            raise ProtocolError("paramiko no instalado. Ejecutar: pip install paramiko")
        
        try:
            port = options.get("port", self.config.get("port", 22))
            user = options.get("user", self.config.get("user"))
            password = options.get("password", self.config.get("password"))
            key_file = options.get("key_file", self.config.get("key_file"))
            show_progress = options.get("progress", True)
            
            is_upload = Path(source).exists()
            
            if is_upload:
                self._upload(source, destination, port, user, password, key_file, show_progress)
            else:
                self._download(source, destination, port, user, password, key_file, show_progress)
                
        except Exception as e:
            logger.error(f"Error en copia SFTP: {e}")
            raise ProtocolError(f"Error en copia SFTP: {e}")

    def _upload(self, source, destination, port, user, password, key_file, show_progress):
        host, remote_path = self._parse_remote(destination)
        ssh = self._connect(host, port, user, password, key_file)
        
        try:
            sftp = ssh.open_sftp()
            src_path = Path(source)
            
            if src_path.is_file():
                total_size = src_path.stat().st_size
                start_time = time.time()
                
                def callback(bytes_transferred, total_bytes):
                    if show_progress:
                        elapsed = time.time() - start_time
                        percent = (bytes_transferred / total_bytes) * 100
                        speed = bytes_transferred / elapsed if elapsed > 0 else 0
                        print(f"\r[{'=' * int(percent/2)}{' ' * (50-int(percent/2))}] {percent:.1f}% - {format_size(bytes_transferred)}/{format_size(total_bytes)} - {format_speed(speed)}", end='', flush=True)
                
                sftp.put(str(src_path), remote_path, callback=callback if show_progress else None)
                
                if show_progress:
                    print()
                    elapsed = time.time() - start_time
                    print(f"✓ Completado: {format_size(total_size)} en {elapsed:.1f}s")
            else:
                self._upload_dir(sftp, src_path, remote_path, show_progress)
            
            sftp.close()
            logger.info("Copia SFTP completada exitosamente")
        finally:
            ssh.close()

    def _download(self, source, destination, port, user, password, key_file, show_progress):
        host, remote_path = self._parse_remote(source)
        ssh = self._connect(host, port, user, password, key_file)
        
        try:
            sftp = ssh.open_sftp()
            dest_path = Path(destination)
            
            try:
                stat = sftp.stat(remote_path)
                total_size = stat.st_size
                start_time = time.time()
                
                def callback(bytes_transferred, total_bytes):
                    if show_progress:
                        elapsed = time.time() - start_time
                        percent = (bytes_transferred / total_bytes) * 100
                        speed = bytes_transferred / elapsed if elapsed > 0 else 0
                        print(f"\r[{'=' * int(percent/2)}{' ' * (50-int(percent/2))}] {percent:.1f}% - {format_size(bytes_transferred)}/{format_size(total_bytes)} - {format_speed(speed)}", end='', flush=True)
                
                sftp.get(remote_path, str(dest_path), callback=callback if show_progress else None)
                
                if show_progress:
                    print()
                    elapsed = time.time() - start_time
                    print(f"✓ Completado: {format_size(total_size)} en {elapsed:.1f}s")
            except IOError:
                self._download_dir(sftp, remote_path, dest_path, show_progress)
            
            sftp.close()
            logger.info("Copia SFTP completada exitosamente")
        finally:
            ssh.close()

    def _upload_dir(self, sftp, local_dir, remote_dir, show_progress):
        try:
            sftp.mkdir(remote_dir)
        except IOError:
            pass
        
        for item in local_dir.iterdir():
            remote_item = f"{remote_dir}/{item.name}"
            if item.is_file():
                if show_progress:
                    print(f"Copiando {item.name}...")
                sftp.put(str(item), remote_item)
            else:
                self._upload_dir(sftp, item, remote_item, show_progress)

    def _download_dir(self, sftp, remote_dir, local_dir, show_progress):
        local_dir.mkdir(parents=True, exist_ok=True)
        
        for item in sftp.listdir_attr(remote_dir):
            remote_item = f"{remote_dir}/{item.filename}"
            local_item = local_dir / item.filename
            
            if self._is_dir(item):
                self._download_dir(sftp, remote_item, local_item, show_progress)
            else:
                if show_progress:
                    print(f"Copiando {item.filename}...")
                sftp.get(remote_item, str(local_item))

    def _connect(self, host, port, user, password, key_file):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        if key_file:
            ssh.connect(host, port=port, username=user, key_filename=key_file)
        elif password:
            ssh.connect(host, port=port, username=user, password=password)
        else:
            ssh.connect(host, port=port, username=user)
        
        return ssh

    def _parse_remote(self, path):
        if "@" in path and ":" in path:
            user_host, remote_path = path.split(":", 1)
            host = user_host.split("@")[1]
            return host, remote_path
        raise ProtocolError(f"Formato inválido: {path}. Usar usuario@host:/ruta")

    def _is_dir(self, attr):
        import stat
        return stat.S_ISDIR(attr.st_mode)
