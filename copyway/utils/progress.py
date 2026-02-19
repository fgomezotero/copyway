"""Utilidades para mostrar progreso de transferencias.

Este módulo proporciona funciones y clases para formatear tamaños,
velocidades y mostrar progreso de transferencias en tiempo real.
"""

import time
import sys
from pathlib import Path
from collections import deque


def get_file_size(path):
    """Obtener tamaño total de archivo o directorio.
    
    Args:
        path (str): Ruta al archivo o directorio
    
    Returns:
        int: Tamaño total en bytes
    
    Example:
        >>> size = get_file_size('/path/to/file.txt')
        >>> print(f"Tamaño: {size} bytes")
    """
    p = Path(path)
    if p.is_file():
        return p.stat().st_size
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())


def format_size(bytes_size):
    """Formatear tamaño en bytes a formato legible.
    
    Args:
        bytes_size (int): Tamaño en bytes
    
    Returns:
        str: Tamaño formateado (ej: "1.5 MB", "500 KB")
    
    Example:
        >>> format_size(1536)
        '1.5 KB'
        >>> format_size(1048576)
        '1.0 MB'
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def format_speed(bytes_per_sec):
    """Formatear velocidad de transferencia.
    
    Args:
        bytes_per_sec (float): Bytes por segundo
    
    Returns:
        str: Velocidad formateada (ej: "1.5 MB/s")
    
    Example:
        >>> format_speed(1048576)
        '1.0 MB/s'
    """
    return f"{format_size(bytes_per_sec)}/s"


class ProgressCallback:
    """Callback para mostrar progreso de transferencias.
    
    Muestra progreso estilo pip con spinner, porcentaje, tamaño y velocidad.
    Cada archivo copiado se muestra en una nueva línea.
    
    Attributes:
        total_size (int): Tamaño total a transferir en bytes
        label (str): Etiqueta para mostrar
        copied (int): Bytes copiados hasta ahora
        start_time (float): Timestamp de inicio
        SPINNER (list): Caracteres del spinner animado
    
    Example:
        >>> progress = ProgressCallback(1048576, "Copiando")
        >>> progress.update(524288, "file1.txt")
        >>> progress.update(524288, "file2.txt")
        >>> progress.finish()
    """
    
    SPINNER = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    
    def __init__(self, total_size, label="Copiando"):
        """Inicializa el callback de progreso.
        
        Args:
            total_size (int): Tamaño total en bytes
            label (str): Etiqueta a mostrar. Default: "Copiando"
        """
        self.total_size = total_size
        self.label = label
        self.copied = 0
        self.start_time = time.time()
        self.last_update = 0
        self.spinner_idx = 0
        self.last_file = None
    
    def update(self, bytes_copied, filename=None):
        """Actualizar progreso de transferencia.
        
        Args:
            bytes_copied (int): Bytes copiados en esta actualización
            filename (str, optional): Nombre del archivo siendo copiado
        """
        self.copied += bytes_copied
        current_time = time.time()
        
        # Mostrar nuevo archivo copiado
        if filename and filename != self.last_file:
            self.last_file = filename
            sys.stdout.write(f"  → {filename}\n")
            sys.stdout.flush()
        
        # Actualizar línea de progreso cada 0.1 segundos
        if current_time - self.last_update < 0.1 and self.copied < self.total_size:
            return
        
        self.last_update = current_time
        self.spinner_idx = (self.spinner_idx + 1) % len(self.SPINNER)
        elapsed = current_time - self.start_time
        
        if elapsed > 0:
            speed = self.copied / elapsed
            percent = (self.copied / self.total_size * 100) if self.total_size > 0 else 0
            
            spinner = self.SPINNER[self.spinner_idx]
            msg = f"\r{spinner} {self.label} {format_size(self.copied)}/{format_size(self.total_size)} ({percent:.0f}%) {format_speed(speed)}"
            
            sys.stdout.write(msg)
            sys.stdout.flush()
    
    def finish(self):
        """Finalizar y mostrar resumen de transferencia.
        
        Muestra el tamaño total, tiempo transcurrido y velocidad promedio.
        """
        elapsed = time.time() - self.start_time
        avg_speed = self.copied / elapsed if elapsed > 0 else 0
        msg = f"\r✓ {self.label} {format_size(self.copied)} en {elapsed:.1f}s ({format_speed(avg_speed)})\n"
        sys.stdout.write(msg)
        sys.stdout.flush()
