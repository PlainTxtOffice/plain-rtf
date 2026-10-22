---
last_updated: 2026-10-21
version: 1.0.1
---

# Build Plain RTF for Windows

Run these commands from the project folder in PowerShell. The scripts also work
from another working directory: relative parameters resolve from the repository
root. They use `.venv/Scripts/python.exe` and metadata from `pyproject.toml`.

```powershell
./scripts/nuitka/standalone.ps1 -Commercial
./scripts/nuitka/onefile.ps1 -Commercial
```

The build interpreter needs the project's dependencies and Nuitka. Use Nuitka
Commercial for distributed builds; `-Commercial` enables its `data-hiding`
plugin. The scripts do not read credentials or install Commercial. The private
installation instructions are named `installing_nuitka.md`; never distribute
that file. A public clone can use free Nuitka by omitting `-Commercial`, with a
warning that program constants are not encrypted.

The tested toolchain is Python 3.14.8, Nuitka 4.3.1 / Commercial 5.10.5,
and MSVC 14.5. Nuitka 4.0.7 failed native compilation with Python 3.14.8;
use a current compatible compiler with this interpreter.

Compressed onefile builds also need `zstandard`, supplied by `Nuitka[onefile]`.
Both builds use `jsonschema` to validate the custom TkDND package configuration.
Install these supporting packages into the selected build environment:

```powershell
.venv/Scripts/python.exe -m pip install jsonschema zstandard
```

Installing `jsonschema` here avoids Nuitka trying to obtain it through the base
Python, which pip's `require-virtualenv` setting can reject even when the build
itself uses `.venv`. Keep that pip protection enabled.

The onefile script checks for `zstandard` before compiling. Both builds use MSVC
(`--msvc=latest`), the `tk-inter` plugin, the application icons, and an explicit
TkDND configuration that adds Windows Tcl 9 DLLs and Tcl scripts. Nuitka may
download its required build tools under `--assume-yes-for-downloads`.

The selected interpreter also supplies the Tcl/Tk library paths. For Python
builds that embed these libraries in Tcl's virtual zip filesystem, the helper
copies only those runtime libraries into a fresh `build/nuitka-inputs/tk-.../`
directory and passes that directory to Nuitka. This avoids depending on a
separate Tcl installation on the recipient's computer.

## Outputs and runtime storage

| Mode | Default build result | Persistent application data |
| --- | --- | --- |
| Onefile | `build/onefile/plain-rtf.exe` | `plain-rtf-data/` beside the executable. |
| Standalone | `build/standalone/main.dist/plain-rtf.exe` plus the rest of `main.dist/` | `%LOCALAPPDATA%/plain-rtf/`. |

The `.dist` directory is named after the `src/main.py` entrypoint. Changing
`OutputFilename` changes the executable name, not the `.dist` directory name.
Document files still go to the locations users choose in the editor.

The portable onefile behavior is an intentional, user-approved departure from
the generic build directions: extraction is beside the executable, not in
Windows temp, and unwritable portable storage never falls back to AppData.
Both extraction and persistent logs stay under the single `plain-rtf-data/`
folder:

```text
plain-rtf.exe
plain-rtf-data/
    logs/
    unpack_<process-id>_<time>/
```

The script anchors extraction with `{PROGRAM_BASE}-data/unpack_{PID}_{TIME}`.
This avoids Nuitka 4.3.1 stripping a leading `{PROGRAM_DIR}` and extracting
relative to the launch directory. The data folder follows the executable's
name: renaming it to `My Notes.exe` uses `My Notes-data/` for both extraction
and logs. Move or rename the existing data folder too if you want to retain
its logs after renaming the executable.

Nuitka removes the per-run `unpack_...` folder on normal exit. Its temporary
mode is explicit; no persistent extraction cache is configured. A crash or
forced termination can leave extracted files behind. The parent data folder
and logs remain. Use a writable folder, including on removable drives. A
read-only location can prevent extraction before the editor starts. If logging
cannot write its data folder, the editor shows a storage error and stops.

Standalone is intended for an installer under Program Files. It does not bundle
`portable.marker`; writable runtime data goes to the user's AppData directory.
Onefile bundles that marker. Neither script bundles local logs, documents,
settings, credentials, tests, or developer data.

These choices control application writes. They do not promise that Windows,
security software, or file dialogs leave no operating-system records.

## Parameters

| Parameter | Default | Purpose |
| --- | --- | --- |
| `PythonExecutable` | `.venv/Scripts/python.exe` | Build interpreter; accepts an absolute path or a repository-relative path. |
| `OutputDirectory` | `build/onefile` or `build/standalone` | Separate output and intermediate-build location for each mode. |
| `OutputFilename` | `plain-rtf.exe`, derived from project metadata | Executable filename only; must end in `.exe`. |
| `Commercial` | Off | Enables Commercial constant encryption; use for distributed builds. |
| `ResetRuntimeDefaults` | Off | Explicitly deletes existing application data for the selected mode before building. |

For example:

```powershell
./scripts/nuitka/onefile.ps1 -Commercial `
    -PythonExecutable 'C:/Build/PythonEnv/Scripts/python.exe' `
    -OutputDirectory 'build/release-onefile' `
    -OutputFilename 'Plain RTF.exe'
```

There is no runtime defaults/settings-file contract in this application, so
`UseCurrentDefaultPaths` is intentionally omitted. `ResetRuntimeDefaults` is
retained for explicit smoke-test cleanup. In standalone mode it deletes
`%LOCALAPPDATA%/plain-rtf/`; in onefile mode it deletes `plain-rtf-data/` under
the selected output directory (using the selected executable's name). This
removes everything in that folder, including any files someone put there
manually. Close running copies first. Without the switch, existing data is only
reported. Cleanup rejects paths outside the selected parent and paths containing
links or junctions.

## Release checks and what to ship

Both scripts scan the uncompressed `.dist` directory after compilation for
the build account's username, repository path, and author emails, in UTF-8 and
UTF-16LE. Executables, DLLs, Python extensions, and common text configuration
files are checked. Each match emits a warning; matches need review and do not
automatically fail the build. This is an identifier scan, not a guarantee that
an artifact contains no sensitive material.

1. Build standalone first and test a copy of `main.dist/`. Never smoke-test the
   release folder itself; runtime files added there could enter an installer.
1. Check opening and saving a note, inline formatting, image insertion, image
   paste, and file drag-and-drop. Verify the expected log location.
1. Build onefile and test a copy of the executable in a separate writable
   folder, preferably with spaces in its name. Confirm `unpack_...` is removed
   on normal exit and that logs remain beside the executable.
1. Review privacy warnings and run the release validator before packaging.

```powershell
pwsh -NoProfile -File scripts/nuitka/validate_release.ps1
```

The validator defaults to `build/standalone/main.dist`. For an overridden
standalone output directory, provide the matching `.dist` path:

```powershell
./scripts/nuitka/validate_release.ps1 -DistPath 'build/release/main.dist'
```

It reports missing output, runtime folders, logs, environment files, and an
unexpected portable marker. It exits with code 1 on problems and never changes
the folder. There is no bundled defaults file requiring an absolute-path check.

For onefile, ship only `plain-rtf.exe`; never include the `plain-rtf-data/`
folder created by testing. For standalone, package the entire checked `.dist`
folder. Never ship `*.build/`, `*.onefile-build/`, compilation report XML files,
or `nuitka-crash-report.xml`. Intermediate directories are kept for later
builds.

## Advanced Installer

Point Advanced Installer at `build/standalone/main.dist/` and install under
Program Files. Add this as a pre-build event with the repository root as its
working directory, and make a nonzero exit code fail the installer build:

```powershell
pwsh -NoProfile -File scripts/nuitka/validate_release.ps1
```

The standalone script also runs that check immediately after its privacy scan.
The pre-build event catches files added to the folder later. Keep
`%LOCALAPPDATA%/plain-rtf/` on uninstall by default so reinstalling preserves
user data. Do not configure the installer to copy or remove that directory.

## References

- [Nuitka distribution modes and onefile extraction](https://nuitka.net/user-documentation/use-cases.html)
- [Nuitka Commercial constant protection](https://nuitka.net/doc/commercial/protect-constants-data.html)
- [TkinterDnD2 and Tcl 9 support](https://pypi.org/project/tkinterdnd2/0.6.4/)
