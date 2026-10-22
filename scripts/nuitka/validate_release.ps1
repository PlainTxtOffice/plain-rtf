[CmdletBinding()]
param([string]$DistPath = 'build/standalone/main.dist')

$ErrorActionPreference = 'Stop'
$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if (-not [IO.Path]::IsPathRooted($DistPath)) {
    $DistPath = Join-Path $repoRoot $DistPath
}
try {
    if (-not (Test-Path -LiteralPath $DistPath -PathType Container)) {
        throw "Distribution folder does not exist: $DistPath"
    }
    # These are the writable roots from src/config/path_handler.py.
    # There is no bundled settings/defaults file in Plain RTF.
    $problems = @()
    foreach ($name in @('logs', 'exports', 'data', 'plain-rtf-data', 'portable.marker')) {
        $path = Join-Path $DistPath $name
        if (Test-Path -LiteralPath $path) {
            $problems += "Unexpected runtime storage or portable marker: $path"
        }
    }
    if (-not (Get-ChildItem -LiteralPath $DistPath -Filter '*.exe' -File)) {
        $problems += "No application executable found in: $DistPath"
    }
    foreach ($file in Get-ChildItem -LiteralPath $DistPath -Recurse -Force -File) {
        if ($file.Extension -eq '.log' -or $file.Name -like '.env*') {
            $problems += "Unexpected log or environment file: $($file.FullName)"
        }
    }
    if ($problems.Count) {
        foreach ($problem in $problems) { Write-Host $problem }
        exit 1
    }
    Write-Host "Release folder is clean: $DistPath"
    exit 0
}
catch {
    Write-Host $_.Exception.Message
    exit 1
}
