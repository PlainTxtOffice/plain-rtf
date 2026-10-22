[CmdletBinding()]
param(
    [string]$PythonExecutable = '.venv/Scripts/python.exe',
    [string]$OutputDirectory = 'build/standalone',
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
Write-Host "Building $($metadata.title) (standalone)"
$outputPath = Resolve-BuildPath $repoRoot $OutputDirectory
$nuitkaArguments = @(New-NuitkaArguments $metadata $outputPath $OutputFilename)
$nuitkaArguments += '--standalone'
if ($Commercial) { $nuitkaArguments += '--enable-plugin=data-hiding' }
else { Write-Warning 'Program constants are not encrypted. Use -Commercial for distribution.' }

$nuitkaArguments += @(New-TkArguments $pythonPath $repoRoot)
Test-RuntimeStorage (Get-UserDataParent) $metadata.storage -ResetRuntimeDefaults:$ResetRuntimeDefaults
[IO.Directory]::CreateDirectory($outputPath) | Out-Null
$nuitkaArguments += 'src/main.py'
$distPath = Join-Path $outputPath 'main.dist'
$validateScript = Join-Path $PSScriptRoot 'validate_release.ps1'
Push-Location $repoRoot
try {
    Write-Host "Output directory: $outputPath"
    & $pythonPath @nuitkaArguments
    if ($LASTEXITCODE -ne 0) { throw "Nuitka standalone build failed (exit $LASTEXITCODE)." }
    Invoke-PrivacyScan $pythonPath $repoRoot $distPath
    & $validateScript -DistPath $distPath
    if ($LASTEXITCODE -ne 0) { throw 'Standalone release validation failed.' }
}
finally { Pop-Location }
