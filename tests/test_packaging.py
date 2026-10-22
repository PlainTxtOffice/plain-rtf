"""Check release safeguards without compiling or deleting real user data."""

import os
import json
import runpy
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = REPO_ROOT / "scripts/nuitka"
PWSH = shutil.which("pwsh")


def test_privacy_scan_encodings_and_chunk_boundary(tmp_path, monkeypatch):
    monkeypatch.setenv("USERNAME", "packaging_test_user")
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nauthors = [{email = "example@example.invalid"}]\n', encoding="utf-8"
    )
    dist = tmp_path / "main.dist"
    dist.mkdir()
    binary = dist / "application.dll"
    binary.write_bytes(b"x" * (1024 * 1024 - 4) + b"packaging_test_user")
    (dist / "settings.txt").write_bytes("example@example.invalid".encode("utf-16le"))
    scan = runpy.run_path(str(SCRIPT_ROOT / "privacy_scan.py"))["scan_output"]
    before = binary.read_bytes()
    hits = scan(tmp_path, dist)
    assert len(hits) == 2
    assert any("packaging_test_user" in hit for hit in hits)
    assert any("example@example.invalid" in hit for hit in hits)
    assert binary.read_bytes() == before
    with pytest.raises(FileNotFoundError):
        scan(tmp_path, tmp_path / "missing")


@pytest.mark.skipif(not PWSH, reason="PowerShell is required")
@pytest.mark.parametrize("unexpected", [None, "logs", "data", "exports", "portable.marker", ".env", "plain-rtf-data"])
def test_release_validation_reports_only(tmp_path, unexpected):
    dist = tmp_path / "main.dist"
    dist.mkdir()
    (dist / "plain-rtf.exe").write_bytes(b"test executable placeholder")
    if unexpected:
        (dist / unexpected).touch()
    before = {p.name: p.read_bytes() for p in dist.iterdir()}
    result = subprocess.run(
        [PWSH, "-NoProfile", "-File", str(SCRIPT_ROOT / "validate_release.ps1"), "-DistPath", str(dist)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == (1 if unexpected else 0), result.stdout + result.stderr
    assert {p.name: p.read_bytes() for p in dist.iterdir()} == before


@pytest.mark.skipif(not PWSH, reason="PowerShell is required")
def test_reset_is_confined_and_explicit(tmp_path):
    (tmp_path / "plain-rtf-data").mkdir()
    (tmp_path / "plain-rtf-data/log.txt").write_text("test", encoding="utf-8")
    (tmp_path / "keep.txt").write_text("keep", encoding="utf-8")
    command = '''
. (Join-Path $env:TEST_SCRIPTS 'runtime_data.ps1')
Test-RuntimeStorage $env:TEST_PARENT 'plain-rtf-data'
if (-not (Test-Path (Join-Path $env:TEST_PARENT 'plain-rtf-data/log.txt'))) { exit 2 }
try {
    Test-RuntimeStorage $env:TEST_PARENT '../outside' -ResetRuntimeDefaults
    exit 3
} catch { }
Test-RuntimeStorage $env:TEST_PARENT 'plain-rtf-data' -ResetRuntimeDefaults
'''
    result = subprocess.run(
        [PWSH, "-NoProfile", "-Command", command], capture_output=True, text=True, check=False,
        env={**os.environ, "TEST_PARENT": str(tmp_path), "TEST_SCRIPTS": str(SCRIPT_ROOT)},
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert not (tmp_path / "plain-rtf-data").exists()
    assert (tmp_path / "keep.txt").read_text(encoding="utf-8") == "keep"


@pytest.mark.skipif(not PWSH, reason="PowerShell is required")
@pytest.mark.parametrize("mode, failure", [
    ("onefile", None), ("standalone", None),
    ("onefile", "compiler"), ("standalone", "compiler"),
    ("onefile", "compression"),
])
def test_build_invocation_and_failure(tmp_path, mode, failure):
    interpreter = tmp_path / "build interpreter.ps1"
    interpreter.write_text('''
if ($args[0] -eq '-c' -and $args[1] -eq 'import zstandard' -and $env:TEST_FAILURE -eq 'compression') {
    exit 7
}
if ($args[0] -eq '-m' -and $args[1] -eq 'nuitka') {
    [IO.File]::WriteAllText($env:TEST_ARGUMENTS, ($args | ConvertTo-Json))
    if ($env:TEST_FAILURE -eq 'compiler') { exit 9 }
    $output = ($args | Where-Object { $_ -like '--output-dir=*' }).Substring(13)
    $dist = Join-Path $output 'main.dist'
    [IO.Directory]::CreateDirectory($dist) | Out-Null
    [IO.File]::WriteAllText((Join-Path $dist 'Custom Name.exe'), 'placeholder')
    exit 0
}
& $env:TEST_PYTHON @args
exit $LASTEXITCODE
''', encoding="utf-8")
    arguments_file = tmp_path / "arguments.json"
    result = subprocess.run(
        [PWSH, "-NoProfile", "-File", str(SCRIPT_ROOT / f"{mode}.ps1"),
         "-PythonExecutable", str(interpreter), "-OutputDirectory", str(tmp_path / "output path"),
         "-OutputFilename", "Custom Name.exe", "-Commercial"],
        cwd=tmp_path, capture_output=True, text=True, check=False,
        env={**os.environ, "TEST_PYTHON": str(REPO_ROOT / ".venv/Scripts/python.exe"),
             "TEST_ARGUMENTS": str(arguments_file), "TEST_FAILURE": failure or "",
             "LOCALAPPDATA": str(tmp_path / "AppData")},
    )
    if failure:
        assert result.returncode != 0
        if failure == "compression":
            assert not arguments_file.exists()
        else:
            assert "build failed" in result.stderr
        return
    assert result.returncode == 0, result.stdout + result.stderr
    arguments = json.loads(arguments_file.read_text(encoding="utf-8"))
    assert f"--{mode}" in arguments
    assert "--enable-plugin=data-hiding" in arguments
    assert "--enable-plugin=tk-inter" in arguments
    assert "--output-filename=Custom Name.exe" in arguments
    assert "--company-name=Plain Text Office LLC" in arguments
    assert "--copyright=Copyright © 2026 Plain Text Office LLC" in arguments
    assert arguments[-1] == "src/main.py"
    marker = "--include-data-files=build/nuitka-inputs/portable.marker=portable.marker"
    if mode == "onefile":
        assert marker in arguments
        assert "--onefile-cache-mode=temporary" in arguments
        assert "--onefile-tempdir-spec={PROGRAM_BASE}-data/unpack_{PID}_{TIME}" in arguments
    else:
        assert marker not in arguments
        assert not any(argument.startswith("--onefile-") for argument in arguments)
