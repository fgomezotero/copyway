import pytest
from unittest.mock import Mock, patch, MagicMock, call
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


class TestSFTPProtocol:
    """Tests for SFTPProtocol, focused on skip-if-same upload logic."""

    def _make_sftp_protocol(self):
        from copyway.protocols.sftp import SFTPProtocol
        return SFTPProtocol()

    # ------------------------------------------------------------------
    # _remote_file_matches
    # ------------------------------------------------------------------

    def test_remote_file_matches_returns_false_when_not_exists(self, tmp_path):
        protocol = self._make_sftp_protocol()
        local_file = tmp_path / "file.txt"
        local_file.write_bytes(b"hello")

        sftp = MagicMock()
        sftp.stat.side_effect = IOError("no such file")

        assert protocol._remote_file_matches(sftp, local_file, "/remote/file.txt") is False

    def test_remote_file_matches_true_when_mtime_within_tolerance(self, tmp_path):
        protocol = self._make_sftp_protocol()
        local_file = tmp_path / "file.txt"
        local_file.write_bytes(b"hello")
        local_mtime = local_file.stat().st_mtime

        sftp = MagicMock()
        remote_stat = MagicMock()
        remote_stat.st_mtime = local_mtime  # same mtime
        sftp.stat.return_value = remote_stat

        assert protocol._remote_file_matches(sftp, local_file, "/remote/file.txt") is True

    def test_remote_file_matches_uses_hash_when_mtime_differs(self, tmp_path):
        """When mtime differs, fall back to hash comparison."""
        protocol = self._make_sftp_protocol()
        content = b"identical content"
        local_file = tmp_path / "file.txt"
        local_file.write_bytes(content)

        sftp = MagicMock()
        remote_stat = MagicMock()
        remote_stat.st_mtime = 0  # differs from local mtime
        sftp.stat.return_value = remote_stat

        # Simulate sftp.open returning the same content
        import io
        sftp.open.return_value.__enter__ = lambda s: io.BytesIO(content)
        sftp.open.return_value.__exit__ = MagicMock(return_value=False)

        with patch.object(protocol, "_remote_hash", return_value=protocol._local_hash(local_file)):
            assert protocol._remote_file_matches(sftp, local_file, "/remote/file.txt") is True

    def test_remote_file_matches_false_when_hash_differs(self, tmp_path):
        protocol = self._make_sftp_protocol()
        local_file = tmp_path / "file.txt"
        local_file.write_bytes(b"local content")

        sftp = MagicMock()
        remote_stat = MagicMock()
        remote_stat.st_mtime = 0  # differs
        sftp.stat.return_value = remote_stat

        with patch.object(protocol, "_remote_hash", return_value="deadbeef"):
            assert protocol._remote_file_matches(sftp, local_file, "/remote/file.txt") is False

    # ------------------------------------------------------------------
    # _upload: skip_if_same=True skips identical files
    # ------------------------------------------------------------------

    @patch("copyway.protocols.sftp.paramiko")
    def test_upload_skips_when_skip_if_same_and_file_matches(self, mock_paramiko, tmp_path, capsys):
        protocol = self._make_sftp_protocol()
        local_file = tmp_path / "file.txt"
        local_file.write_bytes(b"data")

        ssh_mock = MagicMock()
        mock_paramiko.SSHClient.return_value = ssh_mock
        mock_paramiko.AutoAddPolicy.return_value = MagicMock()

        sftp_mock = MagicMock()
        ssh_mock.open_sftp.return_value = sftp_mock

        # Remote path is a file (not a dir)
        file_stat = MagicMock()
        import stat as stat_module
        file_stat.st_mode = stat_module.S_IFREG
        sftp_mock.stat.return_value = file_stat

        with patch.object(protocol, "_remote_file_matches", return_value=True):
            protocol._upload(
                str(local_file),
                "user@host:/remote/file.txt",
                22,
                "user",
                None,
                None,
                True,
                skip_if_same=True,
            )

        sftp_mock.put.assert_not_called()
        captured = capsys.readouterr()
        assert "Omitido" in captured.out

    @patch("copyway.protocols.sftp.paramiko")
    def test_upload_proceeds_when_file_differs(self, mock_paramiko, tmp_path):
        protocol = self._make_sftp_protocol()
        local_file = tmp_path / "file.txt"
        local_file.write_bytes(b"data")

        ssh_mock = MagicMock()
        mock_paramiko.SSHClient.return_value = ssh_mock
        mock_paramiko.AutoAddPolicy.return_value = MagicMock()

        sftp_mock = MagicMock()
        ssh_mock.open_sftp.return_value = sftp_mock

        import stat as stat_module
        file_stat = MagicMock()
        file_stat.st_mode = stat_module.S_IFREG
        sftp_mock.stat.return_value = file_stat

        with patch.object(protocol, "_remote_file_matches", return_value=False):
            protocol._upload(
                str(local_file),
                "user@host:/remote/file.txt",
                22,
                "user",
                None,
                None,
                False,
                skip_if_same=True,
            )

        sftp_mock.put.assert_called_once()

    @patch("copyway.protocols.sftp.paramiko")
    def test_upload_proceeds_when_skip_if_same_false(self, mock_paramiko, tmp_path):
        """Even if files are identical, upload runs when skip_if_same=False."""
        protocol = self._make_sftp_protocol()
        local_file = tmp_path / "file.txt"
        local_file.write_bytes(b"data")

        ssh_mock = MagicMock()
        mock_paramiko.SSHClient.return_value = ssh_mock
        mock_paramiko.AutoAddPolicy.return_value = MagicMock()

        sftp_mock = MagicMock()
        ssh_mock.open_sftp.return_value = sftp_mock

        import stat as stat_module
        file_stat = MagicMock()
        file_stat.st_mode = stat_module.S_IFREG
        sftp_mock.stat.return_value = file_stat

        with patch.object(protocol, "_remote_file_matches", return_value=True):
            protocol._upload(
                str(local_file),
                "user@host:/remote/file.txt",
                22,
                "user",
                None,
                None,
                False,
                skip_if_same=False,
            )

        sftp_mock.put.assert_called_once()
