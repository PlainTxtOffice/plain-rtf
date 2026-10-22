# Creates and builds the persistent Plain RTF Advanced Installer project.
[CmdletBinding()]
param(
    [string]$ProjectRoot = (Join-Path $PSScriptRoot '../..'),
    [string]$SourceDirectory = 'build/standalone/main.dist',
    [string]$PackagingDirectory = 'packaging/advanced-installer',
    [string]$OutputDirectory = 'build/installer',
    [string]$PythonExecutable = '.venv/Scripts/python.exe',
    [string]$AdvancedInstaller = $env:ADVINST_COM
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
. (Join-Path $PSScriptRoot '../nuitka/build_config.ps1')
. (Join-Path $PSScriptRoot 'installer_validation.ps1')

$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$SourceDirectory = Resolve-BuildPath $ProjectRoot $SourceDirectory
$PackagingDirectory = Resolve-BuildPath $ProjectRoot $PackagingDirectory
$OutputDirectory = Resolve-BuildPath $ProjectRoot $OutputDirectory
$pythonPath = Resolve-BuildPath $ProjectRoot $PythonExecutable
$executable = Join-Path $SourceDirectory 'plain-rtf.exe'
if (-not (Test-Path -LiteralPath $executable -PathType Leaf)) { throw "Missing standalone build: $executable" }
if (Test-Path -LiteralPath (Join-Path $SourceDirectory 'portable.marker')) { throw 'Installer payload must not contain portable.marker.' }
if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) { throw "Build interpreter not found: $pythonPath. Override -PythonExecutable." }
$metadata = Read-BuildMetadata $pythonPath $ProjectRoot
$version = [string]$metadata.version
Test-InstallerVersion $version
$architecture = Read-ExeArchitecture $executable
$programFiles = if ($architecture -eq 'x64') { '[ProgramFiles64Folder]' } else { '[ProgramFilesFolder]' }
if ($AdvancedInstaller) { $AdvancedInstaller = $AdvancedInstaller.Trim().Trim('"') }
if (-not $AdvancedInstaller -or -not (Test-Path -LiteralPath $AdvancedInstaller -PathType Leaf) -or
    [IO.Path]::GetFileName($AdvancedInstaller) -ine 'AdvancedInstaller.com') {
    throw 'Set ADVINST_COM or pass -AdvancedInstaller with the path to AdvancedInstaller.com.'
}
$AdvancedInstaller = (Resolve-Path -LiteralPath $AdvancedInstaller).Path
$projectFile = Join-Path $PackagingDirectory 'plain-rtf.aip'
if (Test-Path -LiteralPath $projectFile) {
    Test-InstallerProject $projectFile $SourceDirectory $architecture $metadata.company
}
[IO.Directory]::CreateDirectory($PackagingDirectory) | Out-Null
[IO.Directory]::CreateDirectory($OutputDirectory) | Out-Null

function Invoke-InstallerCli {
    param([string[]]$CliArguments)
    & $AdvancedInstaller @CliArguments
    if ($LASTEXITCODE -ne 0) { throw "Advanced Installer failed ($LASTEXITCODE): $($CliArguments -join ' ')" }
}

if (-not (Test-Path -LiteralPath $projectFile)) {
    # Initialize beside the final AIP to retain its relative source paths.
    $initialProject = Join-Path $PackagingDirectory ('plain-rtf-init-' + [guid]::NewGuid().ToString('N') + '.aip')
    Invoke-InstallerCli @('/newproject', $initialProject, '-type', 'professional', '-lang', 'en')
    Invoke-InstallerCli @('/edit', $initialProject, '/SetProperty', 'ProductName=Plain RTF')
    Invoke-InstallerCli @('/edit', $initialProject, '/SetProperty', "Manufacturer=$($metadata.company)")
    Invoke-InstallerCli @('/edit', $initialProject, '/SetProperty', 'ALLUSERS=1')
    Invoke-InstallerCli @('/edit', $initialProject, '/SetPackageType', $architecture, '-buildname', 'DefaultBuild')
    Invoke-InstallerCli @('/edit', $initialProject, '/SetAppdir', '-buildname', 'DefaultBuild', '-path', ($programFiles + '[Manufacturer]\[ProductName]'))
    Invoke-InstallerCli @('/edit', $initialProject, '/SetShortcutdir', '-buildname', 'DefaultBuild', '-path', '[ProgramMenuFolder]Plain RTF')
    Invoke-InstallerCli @('/edit', $initialProject, '/NewSync', 'APPDIR', $SourceDirectory, '-existingfiles', 'keep')
    Invoke-InstallerCli @('/edit', $initialProject, '/RefreshSync', 'APPDIR')
    Invoke-InstallerCli @('/edit', $initialProject, '/NewShortcut', '-name', 'Plain RTF', '-dir', 'SHORTCUTDIR', '-target', 'APPDIR\plain-rtf.exe', '-wkdir', 'APPDIR')
    Invoke-InstallerCli @('/edit', $initialProject, '/SetOutputType', 'ExeInside', '-buildname', 'DefaultBuild')
    Test-InstallerProject $initialProject $SourceDirectory $architecture $metadata.company
    Move-Item -LiteralPath $initialProject -Destination $projectFile
}

# Preserve the AIP and its UpgradeCode across releases.
Invoke-InstallerCli @('/edit', $projectFile, '/RefreshSync', 'APPDIR')
Test-InstallerProject $projectFile $SourceDirectory $architecture $metadata.company
Invoke-InstallerCli @('/edit', $projectFile, '/SetVersion', $version)
$packageName = "plain-rtf-$version-$architecture-setup.exe"
Invoke-InstallerCli @('/edit', $projectFile, '/SetPackageName', $packageName, '-buildname', 'DefaultBuild')
Invoke-InstallerCli @('/edit', $projectFile, '/SetOutputLocation', '-buildname', 'DefaultBuild', '-path', $OutputDirectory)
$started = [DateTime]::UtcNow
Invoke-InstallerCli @('/rebuild', $projectFile, '-buildslist', 'DefaultBuild')
$artifactPath = Join-Path $OutputDirectory $packageName
if (-not (Test-Path -LiteralPath $artifactPath -PathType Leaf)) { throw "Installer was not produced: $artifactPath" }
$artifact = Get-Item -LiteralPath $artifactPath
if ($artifact.Length -eq 0 -or $artifact.LastWriteTimeUtc -lt $started.AddSeconds(-2)) {
    throw "Installer is empty or was not refreshed by this build: $artifactPath"
}
Write-Host "Project: $projectFile"
$artifact | Select-Object FullName, Length, LastWriteTime
