[CmdletBinding()]
param(
    [string]$PythonExecutable = '.venv/Scripts/python.exe',
    [string]$OutputDirectory = 'build/onefile',
    [string]$OutputFilename = '',
    [switch]$Commercial,
    [switch]$ResetRuntimeDefaults
)

$ErrorActionPreference = 'Stop'
$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
. (Join-Path $PSScriptRoot 'build_config.ps1')
. (Join-Path $PSScriptRoot 'runtime_data.ps1')
$pythonPath = Resolve-BuildPath $repoRoot $PythonExecutable
if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
    throw "Build interpreter not found: $pythonPath. Override -PythonExecutable."
}
$metadata = Read-BuildMetadata $pythonPath $repoRoot
Write-Host "Building $($metadata.title) (onefile)"
$outputPath = Resolve-BuildPath $repoRoot $OutputDirectory
if (-not $OutputFilename) { $OutputFilename = "$($metadata.title).exe" }
$portableDataName = [IO.Path]::GetFileNameWithoutExtension($OutputFilename) + '-data'
$nuitkaArguments = @(New-NuitkaArguments $metadata $outputPath $OutputFilename)
$nuitkaArguments += '--onefile'
# User-approved override: extract beside the EXE, never in Windows temp.
# PID and TIME isolate concurrent runs; temporary mode removes this payload.
# PROGRAM_DIR is stripped by Nuitka 4.3.1; PROGRAM_BASE stays anchored.
$nuitkaArguments += '--onefile-tempdir-spec={PROGRAM_BASE}-data/unpack_{PID}_{TIME}'
$nuitkaArguments += '--onefile-cache-mode=temporary'
if ($Commercial) { $nuitkaArguments += '--enable-plugin=data-hiding' }
else { Write-Warning 'Program constants are not encrypted. Use -Commercial for distribution.' }

& $pythonPath -c 'import zstandard'
if ($LASTEXITCODE -ne 0) {
    throw "Compressed onefile builds require zstandard. Run: `"$pythonPath`" -m pip install 'nuitka[onefile]'"
}
$nuitkaArguments += @(New-TkArguments $pythonPath $repoRoot)
Test-RuntimeStorage $outputPath $portableDataName -ResetRuntimeDefaults:$ResetRuntimeDefaults
[IO.Directory]::CreateDirectory($outputPath) | Out-Null
$inputPath = Join-Path $repoRoot 'build/nuitka-inputs'
[IO.Directory]::CreateDirectory($inputPath) | Out-Null
[IO.File]::WriteAllText((Join-Path $inputPath 'portable.marker'), '')
$nuitkaArguments += '--include-data-files=build/nuitka-inputs/portable.marker=portable.marker'
$nuitkaArguments += 'src/main.py'
$distPath = Join-Path $outputPath 'main.dist'
Push-Location $repoRoot
try {
    Write-Host "Output directory: $outputPath"
    & $pythonPath @nuitkaArguments
    if ($LASTEXITCODE -ne 0) { throw "Nuitka onefile build failed (exit $LASTEXITCODE)." }
    Invoke-PrivacyScan $pythonPath $repoRoot $distPath
}
finally { Pop-Location }
