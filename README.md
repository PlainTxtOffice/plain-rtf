<!-- last_updated: 2026-11-09 -->
<!-- Authoring guidance: dev-docs/specs/README_SPEC.instructions.md -->
<!-- rumdl-disable MD033 MD041 -->
<p align="center">
  <img src="assets/icons/plain_rtf.svg" alt="Plain RTF icon: a document page with the letters Aa" width="96">
</p>

<h1 align="center">Plain RTF</h1>

<p align="center">
  A lightweight editor for formatted notes, saved as plain text you can still
  read in any editor.
</p>

<p align="center">
  <a href="https://github.com/PlainTxtOffice/plain-rtf/releases/latest"><img src="https://img.shields.io/github/v/release/PlainTxtOffice/plain-rtf?label=release" alt="Latest release"></a>
  <a href="#download"><img src="https://img.shields.io/badge/platforms-Windows%20%7C%20Android-informational" alt="Platforms: Windows and Android"></a>
</p>

<p align="center">
  <a href="#download">Download</a> ·
  <a href="docs/USER_MANUAL.md">User manual</a> ·
  <a href="docs/PLAIN_RTF_SPEC.md">Format specification</a> ·
  <a href="https://plaintxtoffice.com/apps/">Website</a>
</p>
<!-- rumdl-enable MD033 MD041 -->

---

## About

Plain RTF is an app for quick notes with text formatting and embedded images,
for Windows and Android. Notes are saved wherever you choose, in a documented
plain-text format.

Documents use the app's own UTF-8 **Plain Text RTF** format, identified by
`PTRTF/1`. They normally have an `.rtf` extension, but they are **not Microsoft
RTF files**. See the [format specification](docs/PLAIN_RTF_SPEC.md) for the
full syntax.

## Features

- Bold, italic, underline, and strikethrough.
- Font families, font sizes, text colors, and background highlighting.
- Bulleted and numbered lists, plus simple text tables.
- Embedded PNG and JPEG images, including image paste on Windows.
- File drag-and-drop and familiar keyboard shortcuts.

## App Screenshot

[![Plain RTF displaying formatted text, a list, and an embedded image](docs/images/plain-rtf-screenshot.jpg)](docs/images/plain-rtf-screenshot.jpg)

*A sample note in Plain RTF on Windows. Click the screenshot to view it full
size.*

## Download

| Platform | Download | Notes |
| --- | --- | --- |
| Windows (portable) | [plain-rtf.exe](https://github.com/PlainTxtOffice/plain-rtf/releases/latest/download/plain-rtf.exe) | Runs without installation. |
| Windows (installer) | [Latest release](https://github.com/PlainTxtOffice/plain-rtf/releases/latest) | Choose the setup executable. |
| Android | [Google Play](https://play.google.com/store/apps/details?id=com.plaintxtoffice.plainrtf) | |

The Windows builds are for x64 (64-bit) and do not need Python installed.

## User Manual

See the [User Manual](docs/USER_MANUAL.md) for setup, usage, keyboard
shortcuts, file-format details, and troubleshooting.

## License

Plain RTF is proprietary software. Copyright (c) 2026 Plain Text Office LLC.
All rights reserved. See [LICENSE](LICENSE) for terms and permission requests.
