"""Run only on a disposable Windows build runner, never on a user's install."""
import ctypes
from contextlib import contextmanager
import os
from pathlib import Path
import subprocess
import sys
import tempfile


@contextmanager
def locked(path):
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateFileW.argtypes = [ctypes.c_wchar_p, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_void_p, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_void_p]
    kernel.CreateFileW.restype = ctypes.c_void_p
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    handle = kernel.CreateFileW(str(path), 0x80000000, 1, None, 3, 0, None)
    assert handle != ctypes.c_void_p(-1).value
    try:
        yield
    finally:
        kernel.CloseHandle(handle)


def main():
    assert os.environ.get("GITHUB_ACTIONS") == "true", "Installer smoke is restricted to a disposable CI runner"
    installer = Path(sys.argv[1]).resolve()
    with tempfile.TemporaryDirectory(prefix="sparkbot-install-smoke-") as directory:
        destination = Path(directory) / "app"
        destination.mkdir()
        connector = destination / "sparkbot-roundtable.exe"
        connector.write_bytes(b"locked sentinel")
        command = [str(installer), "/S", f"/D={destination}"]
        with locked(connector):
            result = subprocess.run(command, timeout=120)
            assert result.returncode != 0, "Installer allowed a locked connector"
            assert connector.read_bytes() == b"locked sentinel"
            assert not (destination / "sparkbot-server.exe").exists()
        result = subprocess.run(command, timeout=180)
        assert result.returncode == 0, "Clean install failed"
        assert (destination / "sparkbot-server.exe").is_file()
        login = subprocess.run([str(connector), "login", "--profile", "ci-cancel"], input=b"", capture_output=True, timeout=15,
                               env={**os.environ, "ROUNDTABLE_HOME": str(Path(directory) / "profiles"), "SPARKBOT_SEAT_KEY": ""})
        assert login.returncode != 0, "Login accepted closed/noninteractive input"
        assert not (Path(directory) / "profiles" / "roundtable-ci-cancel.json").exists()
        uninstall = [str(destination / "uninstall.exe"), "/S", f"_?={destination}"]
        with locked(connector):
            result = subprocess.run(uninstall, timeout=120)
            assert result.returncode != 0, "Uninstaller allowed a locked connector"
            assert connector.is_file() and (destination / "sparkbot-server.exe").is_file()
        result = subprocess.run(uninstall, timeout=120)
        assert result.returncode == 0, "Uninstall after unlocking failed"
        assert not connector.exists() and not (destination / "sparkbot-server.exe").exists()
    print("PASS: locked install/uninstall rejected, clean install/uninstall passed, closed-input login exited without saving a key")


if __name__ == "__main__":
    main()
