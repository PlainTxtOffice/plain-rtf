# Report persisted runtime data, or remove only the explicitly selected root.
Set-StrictMode -Version Latest

function Get-UserDataParent {
    if ($env:LOCALAPPDATA) { return $env:LOCALAPPDATA }
    return Join-Path ([Environment]::GetFolderPath('UserProfile')) 'AppData/Local'
}

function Test-RuntimeStorage {
    param(
        [string]$ParentPath,
        [string]$FolderName,
        [switch]$ResetRuntimeDefaults
    )
    $parent = [IO.Path]::GetFullPath($ParentPath).TrimEnd('\', '/')
    $target = [IO.Path]::GetFullPath((Join-Path $parent $FolderName))
    if ((Split-Path $target -Parent) -ne $parent -or
        (Split-Path $target -Leaf) -ne $FolderName) {
        throw "Refusing to reset a path outside the application storage folder: $target"
    }
    if (-not (Test-Path -LiteralPath $target)) { return }
    if (-not $ResetRuntimeDefaults) {
        Write-Warning "Persisted user data at '$target' may affect smoke tests."
        return
    }
    try {
        if ((Resolve-Path -LiteralPath $target).Path -ne $target) {
            throw 'Unexpected resolved storage path.'
        }
        # Refuse links in the target, its ancestors, or its descendants.
        # Enumerate one level at a time so a junction is never traversed.
        $ancestor = Get-Item -LiteralPath $target -Force
        while ($null -ne $ancestor) {
            if ($ancestor.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                throw 'Storage path contains a link or junction.'
            }
            $ancestor = $ancestor.Parent
        }
        $pending = [Collections.Generic.Queue[string]]::new()
        $pending.Enqueue($target)
        while ($pending.Count -gt 0) {
            foreach ($entry in Get-ChildItem -LiteralPath $pending.Dequeue() -Force) {
                if ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                    throw 'Storage contains a link or junction.'
                }
                if ($entry.PSIsContainer) { $pending.Enqueue($entry.FullName) }
            }
        }
        Remove-Item -LiteralPath $target -Recurse -Force -ErrorAction Stop
    }
    catch {
        throw "Cannot reset '$target'. Close running RTF Editor instances and retry. $($_.Exception.Message)"
    }
}
