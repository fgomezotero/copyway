import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from copyway.protocols.local import LocalProtocol
from copyway.protocols.ssh import SSHProtocol
from copyway.protocols.hdfs import HDFSProtocol
from copyway.exceptions import ProtocolError, ValidationError


class TestLocalProtocol:
    def test_validate_source_not_exists(self, tmp_path):
        protocol = LocalProtocol()
        with pytest.raises(ValidationError):
            protocol.validate("/path/not/exists", str(tmp_path))

    def test_copy_file(self, tmp_path):
        source = tmp_path / "source.txt"
        source.write_text("test")
        dest = tmp_path / "dest.txt"
        
        protocol = LocalProtocol()
        protocol.copy(str(source), str(dest))
        
        assert dest.exists()
        assert dest.read_text() == "test"

    def test_copy_directory(self, tmp_path):
        source = tmp_path / "source_dir"
        source.mkdir()
        (source / "file.txt").write_text("test")
        dest = tmp_path / "dest_dir"
        
        protocol = LocalProtocol()
        protocol.copy(str(source), str(dest))
        
        assert dest.exists()
        assert (dest / "file.txt").exists()


class TestSSHProtocol:
    @patch("subprocess.run")
    def test_copy_basic(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        
        protocol = SSHProtocol()
        protocol.copy("file.txt", "user@host:/path/")
        
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "scp" in args
        assert "-r" in args

    @patch("subprocess.run")
    def test_copy_with_options(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        
        protocol = SSHProtocol()
        protocol.copy("file.txt", "user@host:/path/", port=2222, compress=True)
        
        args = mock_run.call_args[0][0]
        assert "-P" in args
        assert "2222" in args
        assert "-C" in args


class TestHDFSProtocol:
    @patch("subprocess.run")
    def test_copy_basic(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        
        protocol = HDFSProtocol()
        protocol.copy("file.txt", "/hdfs/path/")
        
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "hdfs" in args
        assert "dfs" in args
        assert "-put" in args

    @patch("subprocess.run")
    def test_copy_with_overwrite(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        
        protocol = HDFSProtocol()
        protocol.copy("file.txt", "/hdfs/path/", overwrite=True)
        
        args = mock_run.call_args[0][0]
        assert "-f" in args
