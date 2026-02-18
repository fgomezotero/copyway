import pytest
import tempfile
from pathlib import Path
from copyway.protocols.local import LocalProtocol


class TestLocalFileCopy:
    def test_copy_temp_file_to_temp_dir(self):
        """Test copia de archivo temporal a directorio temporal"""
        protocol = LocalProtocol()
        
        # Crear archivo temporal con contenido
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as src_file:
            src_file.write("Contenido de prueba\n")
            src_file.write("Línea 2\n")
            src_path = src_file.name
        
        # Crear directorio temporal de destino
        with tempfile.TemporaryDirectory() as dest_dir:
            dest_path = Path(dest_dir) / "archivo_copiado.txt"
            
            # Validar y copiar
            protocol.validate(src_path, str(dest_path))
            protocol.copy(src_path, str(dest_path))
            
            # Verificar que el archivo fue copiado
            assert dest_path.exists()
            assert dest_path.is_file()
            
            # Verificar contenido
            content = dest_path.read_text()
            assert "Contenido de prueba" in content
            assert "Línea 2" in content
        
        # Limpiar archivo temporal source
        Path(src_path).unlink()
    
    def test_copy_temp_file_preserves_content(self):
        """Test que la copia preserva el contenido exacto"""
        protocol = LocalProtocol()
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as src:
            original_content = "Test content 123\nÑoño\n🚀"
            src.write(original_content)
            src_path = src.name
        
        with tempfile.TemporaryDirectory() as dest_dir:
            dest_path = Path(dest_dir) / "copy.txt"
            
            protocol.copy(src_path, str(dest_path))
            
            assert dest_path.read_text() == original_content
        
        Path(src_path).unlink()
    
    def test_copy_temp_file_to_existing_dir(self):
        """Test copia a directorio existente (copia dentro del directorio)"""
        protocol = LocalProtocol()
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as src:
            src.write("Log entry")
            src_path = src.name
            src_filename = Path(src_path).name
        
        with tempfile.TemporaryDirectory() as dest_dir:
            # Copiar al directorio (no especificar nombre de archivo)
            protocol.copy(src_path, dest_dir)
            
            # Verificar que se copió con el mismo nombre
            copied_file = Path(dest_dir) / src_filename
            assert copied_file.exists()
            assert copied_file.read_text() == "Log entry"
        
        Path(src_path).unlink()
