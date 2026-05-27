"""Protocolo SFTP para transferencias seguras de archivos.

Implementa transferencias bidireccionales usando paramiko con soporte para
autenticación por password o key file, y progress bar en tiempo real.
"""

import hashlib
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
    def validate(self, source, destination, **options):
        if paramiko is None:
            raise ProtocolError("paramiko no instalado. Ejecutar: pip install paramiko")

        from ..utils.validators import validate_source, validate_destination_sftp

        validate_source(source, "sftp")

        # Pasar credenciales y usuario para validación SFTP
        password = options.get("password", self.config.get("password"))
        key_file = options.get("key_file", self.config.get("key_file"))
        port = options.get("port", self.config.get("port", 22))
        user = options.get("user", self.config.get("user"))

        validate_destination_sftp(destination, password, key_file, port, user)
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
            skip_if_same = options.get("skip_if_same", False)

            is_upload = Path(source).exists()

            if is_upload:
                self._upload(
                    source,
                    destination,
                    port,
                    user,
                    password,
                    key_file,
                    show_progress,
                    skip_if_same,
                )
            else:
                self._download(
                    source, destination, port, user, password, key_file, show_progress
                )

        except Exception as e:
            logger.error(f"Error en copia SFTP: {e}")
            raise ProtocolError(f"Error en copia SFTP: {e}")

    def _upload(
        self, source, destination, port, user, password, key_file, show_progress,
        skip_if_same=False
    ):
        host, remote_path, remote_user = self._parse_remote(destination, user)
        ssh = self._connect(host, port, remote_user, password, key_file)

        try:
            sftp = ssh.open_sftp()
            src_path = Path(source)

            # Verificar si remote_path es un directorio o archivo destino
            try:
                stat = sftp.stat(remote_path)
                # Si existe y es directorio, copiar dentro
                if self._is_dir_stat(stat):
                    remote_path = f"{remote_path}/{src_path.name}"
            except IOError:
                # No existe, verificar si el directorio padre existe
                parent_dir = "/".join(remote_path.rsplit("/", 1)[:-1]) or "/"
                try:
                    sftp.stat(parent_dir)
                except IOError:
                    raise ProtocolError(f"Directorio remoto no existe: {parent_dir}")

            if src_path.is_file():
                if skip_if_same and self._remote_file_matches(sftp, src_path, remote_path):
                    if show_progress:
                        print(f"⏭ Omitido (sin cambios): {remote_path}")
                    logger.info(f"Archivo omitido por ser idéntico: {remote_path}")
                else:
                    total_size = src_path.stat().st_size
                    start_time = time.time()

                    def callback(bytes_transferred, total_bytes):
                        if show_progress:
                            elapsed = time.time() - start_time
                            percent = (bytes_transferred / total_bytes) * 100
                            speed = bytes_transferred / elapsed if elapsed > 0 else 0
                            print(
                                f"\r[{'=' * int(percent/2)}{' ' * (50-int(percent/2))}] {percent:.1f}% - {format_size(bytes_transferred)}/{format_size(total_bytes)} - {format_speed(speed)}",
                                end="",
                                flush=True,
                            )

                    sftp.put(
                        str(src_path),
                        remote_path,
                        callback=callback if show_progress else None,
                    )

                    if show_progress:
                        print()
                        elapsed = time.time() - start_time
                        print(f"✓ Completado: {format_size(total_size)} en {elapsed:.1f}s")
            else:
                self._upload_dir(sftp, src_path, remote_path, show_progress, skip_if_same)

            sftp.close()
            logger.info("Copia SFTP completada exitosamente")
        except IOError as e:
            logger.error(f"Error SFTP: {e}")
            raise ProtocolError(
                f"Error SFTP: {e}. Verifica que el directorio remoto existe y tienes permisos"
            )
        finally:
            ssh.close()

    def _download(
        self, source, destination, port, user, password, key_file, show_progress
    ):
        host, remote_path, remote_user = self._parse_remote(source, user)
        ssh = self._connect(host, port, remote_user, password, key_file)

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
                        print(
                            f"\r[{'=' * int(percent/2)}{' ' * (50-int(percent/2))}] {percent:.1f}% - {format_size(bytes_transferred)}/{format_size(total_bytes)} - {format_speed(speed)}",
                            end="",
                            flush=True,
                        )

                sftp.get(
                    remote_path,
                    str(dest_path),
                    callback=callback if show_progress else None,
                )

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

    def _upload_dir(self, sftp, local_dir, remote_dir, show_progress, skip_if_same=False):
        try:
            sftp.mkdir(remote_dir)
        except IOError:
            pass

        for item in local_dir.iterdir():
            remote_item = "{}/{}".format(remote_dir, item.name)
            if item.is_file():
                if skip_if_same and self._remote_file_matches(sftp, item, remote_item):
                    if show_progress:
                        print(f"⏭ Omitido (sin cambios): {item.name}")
                    logger.info(f"Archivo omitido por ser idéntico: {remote_item}")
                else:
                    if show_progress:
                        print(f"Copiando {item.name}...")
                    sftp.put(str(item), remote_item)
            else:
                self._upload_dir(sftp, item, remote_item, show_progress, skip_if_same)

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

    def _remote_file_matches(self, sftp, local_path, remote_path):
        """Return True if the remote file exists and is identical to the local file.

        Comparison is done in two steps:
        1. modification time (mtime) – if mtimes are within 1 second of each other
           the files are considered identical (tolerates filesystem timestamp
           precision differences between local and remote).
        2. SHA-256 hash – authoritative comparison when mtime differs by more than
           1 second; both local and remote files are hashed and compared.
        """
        try:
            remote_stat = sftp.stat(remote_path)
        except IOError:
            return False  # Remote file does not exist

        local_stat = local_path.stat()

        # Fast path: if mtime matches (within 1-second tolerance), assume equal
        if abs(remote_stat.st_mtime - local_stat.st_mtime) <= 1:
            return True

        # Slow path: compare SHA-256 hashes
        return self._local_hash(local_path) == self._remote_hash(sftp, remote_path)

    @staticmethod
    def _local_hash(path):
        """Compute SHA-256 hash of a local file."""
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def _remote_hash(sftp, remote_path):
        """Compute SHA-256 hash of a remote file via SFTP."""
        h = hashlib.sha256()
        with sftp.open(remote_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

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

    def _parse_remote(self, path, default_user=None):
        if "@" in path and ":" in path:
            user_host, remote_path = path.split(":", 1)
            user = user_host.split("@")[0]
            host = user_host.split("@")[1]
            return host, remote_path, user
        elif ":" in path:
            # Formato host:/ruta, usar --user
            host, remote_path = path.split(":", 1)
            if not default_user:
                raise ProtocolError(
                    f"Debe especificar --user o usar formato usuario@host:/ruta"
                )
            return host, remote_path, default_user
        raise ProtocolError(
            f"Formato inválido: {path}. Usar host:/ruta con --user o usuario@host:/ruta"
        )

    def _is_dir(self, attr):
        import stat

        return stat.S_ISDIR(attr.st_mode)

    def _is_dir_stat(self, stat_result):
        import stat

        return stat.S_ISDIR(stat_result.st_mode)
