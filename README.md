---
last_updated: 2026-10-21
---

<!-- See dev-docs/specs/README_SPEC.md for README generation guidelines -->

# RTF Editor

## Short Description

A super lightweight Plain Text RTF editor.

## Long Description

RTF Editor is a tiny desktop editor for quick rich-text notes on Windows.
It uses tkinter for the GUI with minimal dependencies (Pillow for image support
and tkinterdnd2 for drag-drop). The editor writes Plain Text RTF documents:
UTF-8 `.rtf` files with text styling and embedded images, not Microsoft RTF.

## Usage Examples

```powershell
.venv/Scripts/python.exe -m src.main
```

```powershell
rtf-editor
```

## Code Organization

`src/domains/documents/` owns document models, span operations, embedded-image
normalization, and the native Plain Text RTF codec. Filesystem operations live
in `src/adapters/`; Tk rendering, clipboard integration, and editor interaction
live in `src/gui/`. Domain modules do not depend on the GUI or adapters.

## Glossary

- **Plain Text RTF**: RTF Editor's UTF-8 document format, marked by `PTRTF/1`.
- **Styled text**: Text that includes formatting such as bold, italic, or
  underline.
- **Embedded image**: A PNG or JPEG stored directly in the document file.
- **Unsaved changes**: Edits that exist in the window but have not been written
  to disk yet.
