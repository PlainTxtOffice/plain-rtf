# Input and persistent-project validation for the installer build.
Set-StrictMode -Version Latest

function Test-InstallerVersion {
    param([string]$Version)
    if ($Version -notmatch '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,5}$') {
        throw 'Installer version must have three numeric fields: major.minor.build.'
    }
    $parts = $Version.Split('.') | ForEach-Object { [int]$_ }
    if ($parts[0] -gt 255 -or $parts[1] -gt 255 -or $parts[2] -gt 65535) {
        throw 'Installer version exceeds the Windows Installer limit 255.255.65535.'
    }
}

function Read-ExeArchitecture {
    param([string]$Executable)
    $reader = [IO.BinaryReader]::new([IO.File]::OpenRead($Executable))
    try {
        $stream = $reader.BaseStream
        if ($stream.Length -lt 64 -or $reader.ReadUInt16() -ne 0x5a4d) {
            throw "Invalid DOS header: $Executable"
        }
        $stream.Position = 0x3c
        $offset = $reader.ReadInt32()
        if ($offset -lt 64 -or $offset -gt $stream.Length - 24) {
            throw "Invalid PE header offset: $Executable"
        }
        $stream.Position = $offset
        if ($reader.ReadUInt32() -ne 0x4550) { throw "Invalid PE signature: $Executable" }
        $machine = $reader.ReadUInt16()
    } finally { $reader.Dispose() }
    switch ($machine) {
        0x8664 { return 'x64' }
        0x014c { return 'x86' }
        default { throw ('Unsupported executable architecture: 0x{0:X4}' -f $machine) }
    }
}

function Read-InstallerRows {
    param([xml]$Project, [string]$Component)
    return $Project.SelectNodes("//COMPONENT[@cid='caphyon.advinst.msicomp.$Component']/ROW")
}

function Test-InstallerProject {
    param([string]$ProjectFile, [string]$SourceDirectory, [string]$Architecture, [string]$Manufacturer)
    [xml]$project = Get-Content -LiteralPath $ProjectFile -Raw -Encoding utf8
    $properties = @{}
    Read-InstallerRows $project 'MsiPropsComponent' | ForEach-Object {
        $properties[$_.GetAttribute('Property')] = $_.GetAttribute('Value')
    }
    if ($properties['ProductName'] -ne 'Plain RTF' -or
        $properties['Manufacturer'] -ne $Manufacturer -or
        $properties['ALLUSERS'] -ne '1' -or -not $properties['UpgradeCode']) {
        throw 'The AIP product identity or per-machine installation scope does not match Plain RTF.'
    }
    $build = @(Read-InstallerRows $project 'BuildComponent' | Where-Object { $_.GetAttribute('BuildKey') -eq 'DefaultBuild' })
    if ($build.Count -ne 1 -or $build[0].GetAttribute('MsiPackageType') -ne $Architecture) {
        throw "AIP architecture/build mismatch: expected DefaultBuild with $Architecture. Review the AIP before rebuilding."
    }
    if ($build[0].GetAttribute('PackageType') -ne '1' -or $build[0].GetAttribute('FilesInsideExe') -ne 'true') {
        throw 'DefaultBuild must use EXE output with installation files inside.'
    }
    Test-InstallerSource $project $ProjectFile $SourceDirectory
    Test-InstallerFiles $project
}

function Test-InstallerSource {
    param([xml]$Project, [string]$ProjectFile, [string]$SourceDirectory)
    $sync = @(Read-InstallerRows $Project 'SynchronizedFolderComponent')
    if ($sync.Count -ne 1 -or $sync[0].GetAttribute('Directory_') -ne 'APPDIR') {
        throw 'Expected exactly one synchronized payload folder at APPDIR.'
    }
    $source = Resolve-BuildPath (Split-Path -Parent $ProjectFile) $sync[0].GetAttribute('SourcePath')
    if ($source.TrimEnd('\', '/') -ne $SourceDirectory.TrimEnd('\', '/')) {
        throw "AIP source mismatch: configured '$source', requested '$SourceDirectory'. Update the AIP synchronization source deliberately."
    }
}

function Test-InstallerFiles {
    param([xml]$Project)
    $files = @(Read-InstallerRows $Project 'MsiFilesComponent')
    $duplicates = @($files | Group-Object { $_.GetAttribute('SourcePath') } | Where-Object Count -gt 1)
    if ($duplicates.Count) { throw 'The AIP contains duplicate source files. Repair its imported folder tree before building.' }
    $exe = @($files | Where-Object { ($_.GetAttribute('FileName') -split '\|')[-1] -eq 'plain-rtf.exe' })
    if ($exe.Count -ne 1) { throw 'Expected exactly one plain-rtf.exe in the AIP.' }
    $components = @(Read-InstallerRows $Project 'MsiCompsComponent' | Where-Object {
        $_.GetAttribute('Component') -eq $exe[0].GetAttribute('Component_')
    })
    if ($components.Count -ne 1 -or $components[0].GetAttribute('Directory_') -ne 'APPDIR') {
        throw 'plain-rtf.exe must be installed directly under APPDIR.'
    }
    $target = '[#' + $exe[0].GetAttribute('File') + ']'
    $shortcuts = @(Read-InstallerRows $Project 'MsiShortsComponent' | Where-Object {
        $_.GetAttribute('Directory_') -eq 'SHORTCUTDIR' -and $_.GetAttribute('Target') -eq $target
    })
    if ($shortcuts.Count -ne 1) { throw 'Expected one Start menu shortcut targeting the installed plain-rtf.exe.' }
}
