---
last_updated: 2026-10-21
version: 1.0.0
---

# Build the Plain RTF Installer

Build the release standalone payload first using the
[Nuitka instructions](../nuitka/README.md). The installer script packages the
complete `.dist` folder; it does not compile the application. Build-machine
prerequisites are Advanced Installer Professional (tested with 24.1), the
project virtual environment, and PowerShell. Target PCs do not need Python
installed separately.

```powershell
# Set this to your actual installed version, or pass -AdvancedInstaller.
$env:ADVINST_COM = 'C:\Program Files (x86)\Caphyon\Advanced Installer 24.1\bin\x86\AdvancedInstaller.com'
.\scripts\nuitka\standalone.ps1 -Commercial
.\scripts\advanced_installer\build_installer.ps1
```

The default output is
`build/installer/plain-rtf-<version>-<architecture>-setup.exe`. The script reads
the version and publisher through the same TOML metadata helper as Nuitka.
Versions must contain three numeric fields within the Windows Installer limit
`255.255.65535`. Architecture comes from the payload executable, with x86 and
x64 supported. Recompile after changing the application version or code.

## Paths and Overrides

The repository root defaults to two levels above the script. Relative directory
and Python interpreter overrides resolve against that root, independently of the
shell's working directory.

| Parameter | Default |
| --- | --- |
| `ProjectRoot` | Repository containing this script |
| `SourceDirectory` | `build/standalone/main.dist` |
| `PackagingDirectory` | `packaging/advanced-installer` |
| `OutputDirectory` | `build/installer` |
| `PythonExecutable` | `.venv/Scripts/python.exe` |
| `AdvancedInstaller` | `ADVINST_COM`, pointing to `AdvancedInstaller.com` |

For example, from outside the checkout:

```powershell
& 'C:\Projects\Plain RTF\scripts\advanced_installer\build_installer.ps1' -OutputDirectory 'build/installer review'
```

`-SourceDirectory 'build/release/main.dist'` selects another standalone payload.
For an existing AIP, its synchronization source must already match this path;
otherwise the script stops before editing the project. Update the mapping
deliberately in Advanced Installer's Files and Folders synchronization settings.
Keep references relative to the AIP when possible. Changing architecture also
requires reviewing the existing installer and testing its upgrade behavior.

## Persistent Installer Project

Keep `packaging/advanced-installer/plain-rtf.aip` in source control. The script
creates it only when absent and then reuses it, preserving its UpgradeCode and
authored customizations. Do not delete it to refresh the packaged files. Use
this application's existing AIP for releases; a newly initialized project has a
different installation identity.

The payload is synchronized directly into APPDIR. Do not add the same payload
with `/AddFolder`; that can duplicate its entries. The script rejects duplicate
sources and validates the executable and Start menu shortcut before building.
Synchronization includes added files and removes deleted synchronized files
during refresh.

The installer uses per-machine installation under Program Files and requires
elevation. Plain RTF itself runs as a normal user and keeps writable application
data under `%LOCALAPPDATA%\plain-rtf`. The payload must not contain
`portable.marker`.

Use major upgrades that remove the old version before installing the new
version. Preserve UpgradeCode and increase the application version for each
distributed update. `/SetVersion` generates a new ProductCode when that version
changes. This workflow is not for patches or upgrades that install the new
version before removing the old one. See
[Advanced Installer synchronization guidance](https://docs.advancedinstaller.com/folder-synchronize.html),
[Set Version](https://www.advancedinstaller.com/user-guide/set-version.html),
and
[Microsoft's version limits](https://learn.microsoft.com/en-us/windows/win32/msi/productversion).

Review the AIP diff after a build. Signing remains an AIP configuration concern;
the script does not add a certificate or claim the output is signed. Keep
signing credentials out of source control.

## Release Verification

The script checks native command failures and requires the exact output artifact
to be nonempty and updated by the rebuild. This verifies packaging, not
installation or upgrade behavior.

Before distribution, use a disposable Windows environment without Python to
verify installation, Start menu launch, document open/save, drag-and-drop,
repair, uninstall, and an upgrade from the previous distributed version. Check
that existing user data survives and that the expected installed-product entry
remains. A rebuild of the same version is not an upgrade test.
