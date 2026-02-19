import time
import sys
from pathlib import Path
from collections import deque


def get_file_size(path):
    """Obtener tamaño total de archivo o directorio"""
    p = Path(path)
    if p.is_file():
        return p.stat().st_size
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())


def format_size(bytes_size):
    """Formatear tamaño en bytes a formato legible"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def format_speed(bytes_per_sec):
    """Formatear velocidad de transferencia"""
    return f"{format_size(bytes_per_sec)}/s"


class ProgressCallback:
    """Callback estilo pip - muestra cada archivo en nueva línea"""
    
    SPINNER = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    
    def __init__(self, total_size, label="Copiando"):
        self.total_size = total_size
        self.label = label
        self.copied = 0
        self.start_time = time.time()
        self.last_update = 0
        self.spinner_idx = 0
        self.last_file = None
    
    def update(self, bytes_copied, filename=None):
        """Actualizar progreso"""
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
        """Finalizar progreso"""
        elapsed = time.time() - self.start_time
        avg_speed = self.copied / elapsed if elapsed > 0 else 0
        msg = f"\r✓ {self.label} {format_size(self.copied)} en {elapsed:.1f}s ({format_speed(avg_speed)})\n"
        sys.stdout.write(msg)
        sys.stdout.flush()
