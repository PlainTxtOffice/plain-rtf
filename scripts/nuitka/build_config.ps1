# Shared metadata and Nuitka arguments for the two build entrypoints.
Set-StrictMode -Version Latest

function Resolve-BuildPath {
    param([string]$RepoRoot, [string]$Path)
    if ([IO.Path]::IsPathRooted($Path)) {
        return [IO.Path]::GetFullPath($Path)
    }
    return [IO.Path]::GetFullPath((Join-Path $RepoRoot $Path))
}

function Read-BuildMetadata {
    param([string]$PythonPath, [string]$RepoRoot)
    $reader = @'
import json, pathlib, sys, tomllib
root = pathlib.Path(sys.argv[1])
metadata = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
project = metadata.get("project", {})
settings = metadata["tool"]["plain-rtf"]
print(json.dumps({
    "title": project.get("name") or root.name,
    "description": project.get("description") or root.name,
    "version": project["version"],
    "storage": settings["app-data-dir"],
    "company": settings["company-name"],
    "copyright": settings["copyright"],
}))
'@
    $json = & $PythonPath -c $reader $RepoRoot
    if ($LASTEXITCODE -ne 0) { throw 'Could not read pyproject.toml build metadata.' }
    $metadata = $json | ConvertFrom-Json
    if ($metadata.version -notmatch '^\d+(\.\d+){0,3}$') {
        throw 'Windows version must contain one to four numeric components.'
    }
    if ($metadata.storage -notmatch '^[a-zA-Z0-9][a-zA-Z0-9_-]*$') {
        throw 'app-data-dir must be a simple folder name.'
    }
    foreach ($field in @('company', 'copyright', 'title', 'description')) {
        if ([string]::IsNullOrWhiteSpace($metadata.$field)) {
            throw "Missing build metadata: $field."
        }
    }
    return $metadata
}

function New-NuitkaArguments {
    param($Metadata, [string]$OutputPath, [string]$OutputFilename)
    if (-not $OutputFilename) { $OutputFilename = "$($Metadata.title).exe" }
    if ($OutputFilename -match '[\\/:*?"<>|]' -or
        -not $OutputFilename.EndsWith('.exe', [StringComparison]::OrdinalIgnoreCase)) {
        throw 'OutputFilename must be an .exe filename without a directory.'
    }
    return @(
        '-m', 'nuitka',
        '--enable-plugin=tk-inter',
        '--include-package=src',
        '--windows-console-mode=disable',
        '--windows-icon-from-ico=assets/rtf_editor_icon.ico',
        '--include-data-files=assets/rtf_editor_icon.ico=assets/rtf_editor_icon.ico',
        '--include-data-files=assets/rtf_editor_icon.png=assets/rtf_editor_icon.png',
        '--user-package-configuration-file=scripts/nuitka/tkdnd.nuitka-package.config.yml',
        '--msvc=latest',
        '--assume-yes-for-downloads',
        "--output-filename=$OutputFilename",
        "--output-dir=$OutputPath",
        "--report=$(Join-Path $OutputPath 'compilation-report.xml')",
        "--product-name=$($Metadata.title)",
        "--file-version=$($Metadata.version)",
        "--product-version=$($Metadata.version)",
        "--file-description=$($Metadata.description)",
        "--company-name=$($Metadata.company)",
        "--copyright=$($Metadata.copyright)"
    )
}

function Invoke-PrivacyScan {
    param([string]$PythonPath, [string]$RepoRoot, [string]$DistPath)
    $scanner = Join-Path $PSScriptRoot 'privacy_scan.py'
    $hits = & $PythonPath $scanner $RepoRoot $DistPath
    if ($LASTEXITCODE -ne 0) { throw 'The post-build privacy scan failed.' }
    foreach ($hit in $hits) { Write-Warning $hit }
}

function New-TkArguments {
    param([string]$PythonPath, [string]$RepoRoot)
    $preparer = Join-Path $PSScriptRoot 'tk_libraries.py'
    $inputs = Join-Path $RepoRoot 'build/nuitka-inputs'
    $json = & $PythonPath $preparer $inputs
    if ($LASTEXITCODE -ne 0) { throw 'Could not prepare Tcl/Tk runtime libraries.' }
    $libraries = $json | ConvertFrom-Json
    foreach ($entry in @(@($libraries.tcl, 'init.tcl'), @($libraries.tk, 'dialog.tcl'))) {
        if (-not (Test-Path -LiteralPath (Join-Path $entry[0] $entry[1]) -PathType Leaf)) {
            throw "Tcl/Tk runtime library is incomplete: $($entry[0])"
        }
    }
    return @("--tcl-library-dir=$($libraries.tcl)", "--tk-library-dir=$($libraries.tk)")
}
