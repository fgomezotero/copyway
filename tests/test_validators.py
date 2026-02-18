import pytest
import tempfile
from pathlib import Path
from copyway.utils.validators import validate_source, validate_destination, validate_disk_space, _format_size
from copyway.exceptions import ValidationError


class TestValidators:
    def test_validate_source_exists(self, tmp_path):
        file = tmp_path / "test.txt"
        file.write_text("test")
        assert validate_source(str(file), "local") is True
    
    def test_validate_source_not_exists(self):
        with pytest.raises(ValidationError, match="Source no existe"):
            validate_source("/path/not/exists", "local")
    
    def test_validate_destination_dir_exists(self, tmp_path):
        assert validate_destination(str(tmp_path), "local") is True
    
    def test_validate_destination_new_file(self, tmp_path):
        new_file = tmp_path / "new.txt"
        assert validate_destination(str(new_file), "local") is True
    
    def test_validate_destination_file_exists(self, tmp_path):
        file = tmp_path / "exists.txt"
        file.write_text("test")
        with pytest.raises(ValidationError, match="ya existe como archivo"):
            validate_destination(str(file), "local")
    
    def test_validate_destination_parent_not_exists(self):
        with pytest.raises(ValidationError, match="Directorio padre no existe"):
            validate_destination("/nonexistent/dir/file.txt", "local")
    
    def test_validate_disk_space_sufficient(self, tmp_path):
        file = tmp_path / "small.txt"
        file.write_text("small")
        dest = tmp_path / "dest.txt"
        assert validate_disk_space(str(file), str(dest), "local") is True
    
    def test_format_size_bytes(self):
        assert _format_size(500) == "500.00 B"
    
    def test_format_size_kb(self):
        assert _format_size(2048) == "2.00 KB"
    
    def test_format_size_mb(self):
        assert _format_size(5 * 1024 * 1024) == "5.00 MB"
    
    def test_format_size_gb(self):
        assert _format_size(3 * 1024 * 1024 * 1024) == "3.00 GB"
    
    def test_validate_source_ssh_local(self, tmp_path):
        file = tmp_path / "test.txt"
        file.write_text("test")
        assert validate_source(str(file), "ssh") is True
    
    def test_validate_source_ssh_remote(self):
        assert validate_source("user@host:/path/file.txt", "ssh") is True
    
    def test_validate_source_hdfs_local(self, tmp_path):
        file = tmp_path / "test.txt"
        file.write_text("test")
        assert validate_source(str(file), "hdfs") is True
    
    def test_validate_source_hdfs_remote(self):
        assert validate_source("hdfs://namenode/path", "hdfs") is True
