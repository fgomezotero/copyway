import os
import subprocess
from pathlib import Path
from ..exceptions import ValidationError
from ..utils.logger import logger


def validate_source(source, protocol="local"):
    if protocol == "local":
        if not Path(source).exists():
            raise ValidationError(f"Source no existe: {source}")
    elif protocol == "ssh" or protocol == "sftp":
        # Validar formato usuario@host:/ruta
        if "@" not in source and ":" not in source:
            # Es ruta local, validar que existe
            if not Path(source).exists():
                raise ValidationError(f"Source local no existe: {source}")
    elif protocol == "hdfs":
        # Si es ruta local, validar que existe
        if not source.startswith("hdfs://") and not source.startswith("/"):
            if not Path(source).exists():
                raise ValidationError(f"Source local no existe: {source}")
    return True


def validate_destination_sftp(
    destination, password=None, key_file=None, port=22, user=None
):
    """Validación específica para SFTP con credenciales"""
    if "@" in destination and ":" in destination:
        host_part = destination.split(":")[0]
        try:
            import paramiko

            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            host = host_part.split("@")[1]
            remote_user = host_part.split("@")[0]

            if key_file:
                ssh.connect(
                    host,
                    port=port,
                    username=remote_user,
                    key_filename=key_file,
                    timeout=15,
                )
            elif password:
                ssh.connect(
                    host, port=port, username=remote_user, password=password, timeout=15
                )
            else:
                ssh.connect(host, port=port, username=remote_user, timeout=15)

            ssh.close()
        except ImportError:
            raise ValidationError(
                "paramiko no instalado. Ejecutar: pip install paramiko"
            )
        except Exception as e:
            raise ValidationError(f"No se puede conectar a {host_part}: {e}")
    elif ":" in destination:
        # Formato host:/ruta con --user
        if not user:
            raise ValidationError(
                "Debe especificar --user o usar formato usuario@host:/ruta"
            )
        host = destination.split(":")[0]
        try:
            import paramiko

            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if key_file:
                ssh.connect(
                    host, port=port, username=user, key_filename=key_file, timeout=15
                )
            elif password:
                ssh.connect(
                    host, port=port, username=user, password=password, timeout=15
                )
            else:
                ssh.connect(host, port=port, username=user, timeout=15)

            ssh.close()
        except ImportError:
            raise ValidationError(
                "paramiko no instalado. Ejecutar: pip install paramiko"
            )
        except Exception as e:
            raise ValidationError(f"No se puede conectar a {host}: {e}")
    return True


def validate_destination(destination, protocol="local"):
    if protocol == "local":
        dest = Path(destination)

        # Si destination es un directorio existente, está OK (se copiará dentro)
        if dest.exists() and dest.is_dir():
            # Validar permisos de escritura en el directorio
            if not os.access(dest, os.W_OK):
                raise ValidationError(f"Sin permisos de escritura en: {dest}")
            return True

        # Si destination no existe, validar que el directorio padre existe y tiene permisos
        if not dest.exists():
            parent = dest.parent
            if not parent.exists():
                raise ValidationError(f"Directorio padre no existe: {parent}")
            if not os.access(parent, os.W_OK):
                raise ValidationError(f"Sin permisos de escritura en: {parent}")
            return True

        # Si destination existe como archivo, error
        if dest.is_file():
            raise ValidationError(f"Destination ya existe como archivo: {destination}")
    elif protocol == "ssh":
        # Validar conectividad SSH si es destino remoto
        if "@" in destination and ":" in destination:
            host_part = destination.split(":")[0]
            try:
                result = subprocess.run(
                    [
                        "ssh",
                        "-o",
                        "ConnectTimeout=5",
                        "-o",
                        "BatchMode=yes",
                        host_part,
                        "echo",
                        "ok",
                    ],
                    capture_output=True,
                    timeout=10,
                )
                if result.returncode != 0:
                    raise ValidationError(
                        f"No se puede conectar a {host_part}. Verificar SSH."
                    )
            except subprocess.TimeoutExpired:
                raise ValidationError(f"Timeout conectando a {host_part}")
            except FileNotFoundError:
                raise ValidationError("Comando 'ssh' no encontrado")
    elif protocol == "sftp":
        # Validar conectividad SFTP si es destino remoto
        if "@" in destination and ":" in destination:
            host_part = destination.split(":")[0]
            try:
                import paramiko

                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                host = host_part.split("@")[1]
                user = host_part.split("@")[0]
                ssh.connect(host, username=user, timeout=15)
                ssh.close()
            except ImportError:
                raise ValidationError(
                    "paramiko no instalado. Ejecutar: pip install paramiko"
                )
            except Exception as e:
                raise ValidationError(f"No se puede conectar a {host_part}: {e}")
    elif protocol == "hdfs":
        # Validar que hdfs está disponible (pero permitir en pruebas sin Hadoop)
        try:
            subprocess.run(
                ["hdfs", "version"], capture_output=True, check=True, timeout=5
            )
        except FileNotFoundError:
            # En ambiente de pruebas o sin Hadoop instalado, solo logear warning
            # En producción, el usuario sabrá si necesita HDFS
            logger.debug(
                "Comando 'hdfs' no encontrado. Hadoop puede no estar instalado."
            )
        except subprocess.CalledProcessError:
            logger.debug("Error ejecutando 'hdfs'. Verificar configuración.")
        except subprocess.TimeoutExpired:
            logger.debug("Timeout ejecutando 'hdfs'.")
    return True


def validate_disk_space(source, destination, protocol="local"):
    if protocol == "local":
        src = Path(source)
        if src.is_file():
            size = src.stat().st_size
        else:
            size = sum(f.stat().st_size for f in src.rglob("*") if f.is_file())

        dest_stat = os.statvfs(Path(destination).parent)
        available = dest_stat.f_bavail * dest_stat.f_frsize

        if size > available:
            raise ValidationError(
                f"Espacio insuficiente. Requerido: {_format_size(size)}, "
                f"Disponible: {_format_size(available)}"
            )
    return True


def _format_size(bytes_size):
    """Formatear tamaño en bytes a formato legible"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"
