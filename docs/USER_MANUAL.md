---
last_updated: 2026-11-22
version: 6.0.0
product_versions:
  windows: "0.1.0"
  ios: "1.0.1"
  android: "1.0.2"
generated_from: "dev-docs/specs/USER_MANUAL_SPEC.instructions.md"
---

# User Manual

## Overview

Plain RTF is an editor for people writing quick rich-text notes on Windows,
Android, and iOS. It supports text formatting, lists, simple tables, and
embedded images through a graphical interface. On Windows it is a desktop
program, named **RTF Editor** in its window, which can also be started from a
terminal. On Android and iPhone it is an app named **Plain RTF**. This manual
covers installation and everyday use on all three. The iOS app offers fewer
editing commands than the others; each task below says what it lacks.
<!-- Verified from: platform/windows/pyproject.toml [project]; platform/windows/plain_rtf/gui/menus/help.py [ABOUT_TEXT]; platform/windows/plain_rtf/main.py [main]; platform/android/app/src/main/res/values/strings.xml [app_name, help_about_body]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/PlainRtfApp.kt [PlainRtfApp]; platform/ios/plain_rtf.xcodeproj/project.pbxproj [INFOPLIST_KEY_CFBundleDisplayName, TARGETED_DEVICE_FAMILY]; platform/ios/plain_rtf/FormatToolbar.swift [FormatToolbar] -->

Documents use the application's **Plain Text RTF** format. Although filenames
normally end in `.rtf`, these are UTF-8 text files beginning with `PTRTF/1`.
They are not Microsoft RTF documents and cannot be exchanged as Microsoft RTF.
<!-- Verified from: platform/windows/plain_rtf/gui/menus/help.py [RTF_SUPPORT_TEXT]; platform/windows/plain_rtf/domains/documents/plain_text_rtf.py [FORMAT_HEADER, parse_plain_text_rtf]; platform/ios/plain_rtf/PlainTextRTF.swift [header, parse] -->

## Installation and Setup

| Platform | Requirements | Where to get it |
| --- | --- | --- |
| Windows | An x64 (64-bit) PC. | [Latest release](https://github.com/PlainTxtOffice/plain-rtf/releases/latest) |
| Android | Android 9 or later. | [Google Play](https://play.google.com/store/apps/details?id=com.plaintxtoffice.plainrtf) |
| iOS | An iPhone with iOS 26.4 or later. | [App Store](https://apps.apple.com/app/id6837573461) |
<!-- Verified from: README.md [Download]; platform/windows/scripts/advanced_installer/build_installer.ps1 [Read-ExeArchitecture]; platform/android/app/build.gradle.kts [applicationId, minSdk]; platform/ios/plain_rtf.xcodeproj/project.pbxproj [IPHONEOS_DEPLOYMENT_TARGET, TARGETED_DEVICE_FAMILY]; dev-docs/store_listings/app-store.md [Status] -->

### Install on Windows

The release offers two downloads. Use either one:

- `plain-rtf-setup.exe` installs the program on the computer.
- `plain-rtf.exe` is a portable program that runs without installation.

To use the installer:

1. Download `plain-rtf-setup.exe` from the latest release.
1. Run it and follow its prompts. It needs administrator permission, and it
   installs the program for every user of the computer under `Program Files`.
1. Find the program in the **Plain RTF** folder of the Start menu.

To use the portable program:

1. Download `plain-rtf.exe` from the latest release.
1. Move it to a folder you are allowed to write to. It keeps its diagnostic
   log in a `plain-rtf-data/` folder beside itself.
<!-- Verified from: README.md [Download]; platform/windows/scripts/advanced_installer/README.md [Persistent Installer Project]; platform/windows/packaging/advanced-installer/plain-rtf.aip [ALLUSERS, SET_APPDIR, SET_SHORTCUTDIR, Shortcut]; platform/windows/plain_rtf/config/path_handler.py [_look_runtime_storage] -->

### Install on Android

1. Open
   [Plain RTF on Google Play](https://play.google.com/store/apps/details?id=com.plaintxtoffice.plainrtf).
1. Install the app.

The app does not request internet access.
<!-- Verified from: README.md [Download]; platform/android/app/build.gradle.kts [applicationId]; platform/android/app/src/main/AndroidManifest.xml; platform/android/app/src/main/res/values/strings.xml [privacy_services_body] -->

### Install on iOS

1. On your iPhone, open
   [Plain RTF on the App Store](https://apps.apple.com/app/id6837573461).
1. Install the app.

The app has no account, advertising, or analytics service.
<!-- Verified from: README.md [Download]; dev-docs/store_listings/app-store.md [Status]; platform/ios/plain_rtf.xcodeproj/project.pbxproj [PRODUCT_BUNDLE_IDENTIFIER, INFOPLIST_KEY_CFBundleDisplayName]; platform/ios/plain_rtf/PrivacyPolicyView.swift [PrivacyPolicyView] -->

## Starting the Program

### Start on Windows

Open **Plain RTF** from the Start menu if you used the installer, or
double-click the portable `plain-rtf.exe`. The program opens an empty document
titled **Untitled - RTF Editor**. The status bar shows **New document** and
**0 characters**.
<!-- Verified from: platform/windows/packaging/advanced-installer/plain-rtf.aip [Shortcut]; platform/windows/plain_rtf/main.py [main]; platform/windows/plain_rtf/gui/views/root_window.py [__init__, _update_title, _set_saved_state, _update_char_count] -->

To open an existing document immediately, start the program from a terminal
and supply the document's path as the first argument. Run the command from the
folder that holds `plain-rtf.exe`; the installer's default is
`C:/Program Files/Plain Text Office LLC/Plain RTF/`. Quote paths containing
spaces:

```powershell
./plain-rtf.exe "C:/Users/YourName/Documents/My notes.rtf"
```

Use an existing Plain Text RTF file. Relative paths are relative to the folder
from which you launch the command. An unsuccessful startup open shows
**Open failed** and leaves an empty document available.
<!-- Verified from: platform/windows/pyproject.toml [executable-name]; platform/windows/packaging/advanced-installer/plain-rtf.aip [SET_APPDIR, File plain-rtf.exe]; platform/windows/plain_rtf/main.py [_get_startup_path]; platform/windows/plain_rtf/adapters/files.py [read_rtf]; platform/windows/plain_rtf/gui/views/root_window.py [__init__, _open_path] -->

To quit, choose **File > Exit** or close the window. If prompted to save,
choose **Yes** to save first, **No** to discard unsaved changes, or **Cancel**
to keep working. Canceling the save dialog or failing to save also stops the
close operation.
<!-- Verified from: platform/windows/plain_rtf/gui/menus/file.py [build_file_menu]; platform/windows/plain_rtf/gui/views/root_window.py [_on_close, _prompt_for_unsaved_changes, _save_document_as] -->

### Start on Android

Tap the **Plain RTF** icon. The Home screen offers **Create New Document** and
**Open Existing**, and lists any **Recovery drafts**. You can also open an
`.rtf` file from another app, such as a file manager, and choose Plain RTF
when Android offers it. Unsaved changes in a document that was already open
stay in its recovery draft.
<!-- Verified from: platform/android/app/src/main/AndroidManifest.xml [intent-filter]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/MainActivity.kt [openViewedDocument]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/AppViewModel.kt [openExternal]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/home/HomeScreen.kt [HomeScreen] -->

To leave a document, tap **Back** in the top bar. If it has unsaved changes,
choose **Save**, **Keep Draft and Close**, **Discard Changes**, or **Cancel**.
There is no quit command; leave the app as you leave any Android app. Unsaved
changes are written to a recovery draft when the app leaves the screen.
<!-- Verified from: platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/editor/EditorScreen.kt [EditorScreen, CloseWarningDialog]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/AppViewModel.kt [closeIfSaved, keepDraftAndClose, discardAndClose, onAppStopped] -->

### Start on iOS

Tap the **Plain RTF** icon. The Home screen offers **Create New Document** and
**Open Existing**, and lists each recovery draft as a **Recover:** button
followed by the document's name. Documents cannot be opened from other apps;
use **Open Existing**.
<!-- Verified from: platform/ios/plain_rtf/HomeView.swift [HomeView]; platform/ios/plain_rtf.xcodeproj/project.pbxproj [GENERATE_INFOPLIST_FILE] -->

To leave a document, tap **Back** at the top left. If it has unsaved changes,
**Unsaved changes** offers **Keep Draft and Close**, **Discard Changes**, or
**Cancel**. To save instead, choose **Cancel** and tap **Save** first. There is
no quit command; leave the app as you leave any iPhone app. Unsaved changes are
written to a recovery draft when the app leaves the screen.
<!-- Verified from: platform/ios/plain_rtf/EditorView.swift [EditorView]; platform/ios/plain_rtf/RTFDocument.swift [persistDraft, discardDraft] -->

## Getting Around

Plain RTF holds one document at a time. Click or tap in the main text area to
place the insertion cursor, type, or select text. Text wraps at word boundaries;
scroll to move through a longer document.
<!-- Verified from: platform/windows/plain_rtf/gui/views/root_window.py [_build_editor, _load_document]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/AppViewModel.kt [activate]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/editor/EditorScreen.kt [EditorScreen] -->

The Windows window has these areas:

| Area | What it tells you or lets you do |
| --- | --- |
| Title bar | Shows the current filename, or **Untitled**. A leading `*` marks unsaved changes. |
| **File** menu | Create, open, save, rename through **Save As...**, or exit. |
| **Format** menu | Format selected text, change list markers, and insert tables or images. |
| **Help** menu | Open **Keyboard Shortcuts**, **RTF Support**, or **About RTF Editor**. |
| Status bar, left | Reports actions and hints, such as **Unsaved changes** or **Opened notes.rtf**. |
| Status bar, right | Counts document characters; each embedded image counts as one. |
<!-- Verified from: platform/windows/plain_rtf/gui/menus/file.py [build_file_menu]; platform/windows/plain_rtf/gui/menus/format.py [build_format_menu]; platform/windows/plain_rtf/gui/menus/help.py [build_help_menu]; platform/windows/plain_rtf/gui/views/root_window.py [_update_title, _build_status_bar, _update_char_count] -->

The Android app has a Home screen and an editor screen:

| Area | What it tells you or lets you do |
| --- | --- |
| Home screen | **Create New Document**, **Open Existing**, and the **Recovery drafts** list. The icons at the top open **Help**, **Send feedback**, and **Privacy**. |
| Editor top bar | **Back**, the document name, which you can tap to change, **Save**, and **More options** with **Save As…**, **Help**, and **Send feedback**. |
| Status line, left | Reports actions, such as **Unsaved changes** or **Saved notes**. |
| Status line, right | Counts document characters. |
| Format toolbar | Sits below the status line and scrolls sideways: **Undo**, **Redo**, **Bold**, **Italic**, **Underline**, **Strikethrough**, **Font**, **Font size**, **Text color**, **Background color**, **Bullet list**, **Numbered list**, **Insert tab**, **Insert table**, and **Insert image**. |
<!-- Verified from: platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/home/HomeScreen.kt [HomeScreen]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/editor/EditorScreen.kt [EditorScreen, DocumentTitleField, OverflowMenu, EditorStatusBar]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/editor/FormatToolbar.kt [FormatToolbar]; platform/android/app/src/main/res/values/strings.xml -->

The iOS app also has a Home screen and an editor screen:

| Area | What it tells you or lets you do |
| --- | --- |
| Home screen | **Create New Document**, **Open Existing**, and a **Recover:** button for each recovery draft. The buttons at the top open **Privacy** and **Send Feedback**. |
| Editor top bar | **Back**, the document name, which you can tap to rename, and **Save** (the tray with a downward arrow). |
| Bottom of the editor | Shows **Unsaved** while the document has unsaved changes. |
| Format toolbar | Sits above the keyboard and scrolls sideways: **Bold**, **Italic**, **Underline**, **Font Size**, **Text Color**, and **Lists**. |
<!-- Verified from: platform/ios/plain_rtf/HomeView.swift [HomeView]; platform/ios/plain_rtf/PrivacyPolicyView.swift [PrivacyPolicyButton]; platform/ios/plain_rtf/EditorView.swift [EditorView]; platform/ios/plain_rtf/RichTextEditor.swift [makeUIView]; platform/ios/plain_rtf/FormatToolbar.swift [FormatToolbar] -->

In the task steps below, menu paths such as **Format > Bold** are the Windows
route. On Android and iOS, use the toolbar button or top-bar command named in
each task.

## Everyday Tasks

### Create and edit a note

1. Choose **File > New**, or press **Ctrl+N**.
1. Resolve the save prompt if your current document has unsaved changes.
1. Type in the empty text area. Press **Enter** for a new line.
1. Select existing text to replace it by typing, or remove it with **Delete**.
1. Save the note with **File > Save**.

On Windows, the title begins with `*` after an edit. Starting a new document
replaces the current document and clears its undo history. **Cancel** at the
unsaved-changes prompt keeps the current document open.
<!-- Verified from: platform/windows/plain_rtf/gui/views/root_window.py [_new_file, _build_editor, _handle_return, _handle_modified, _load_document, _prompt_for_unsaved_changes] -->

On Android, tap **Create New Document** on the Home screen, and save with
**Save** in the top bar. The new note is named **Untitled**; tap the name to
change it. The status line reads **Unsaved changes** after an edit.
<!-- Verified from: platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/home/HomeScreen.kt [HomeScreen]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/AppViewModel.kt [newDocument]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/domain/session/DocumentSession.kt [DEFAULT_DOCUMENT_NAME, rename]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/editor/EditorScreen.kt [DocumentTitleField, EditorStatusBar] -->

On iOS, tap **Create New Document** on the Home screen, and save with **Save**
in the top bar. The new note is named **Untitled**; tap the name at the top to
rename it. **Unsaved** appears at the bottom of the screen after an edit.
<!-- Verified from: platform/ios/plain_rtf/HomeView.swift [HomeView]; platform/ios/plain_rtf/RTFDocument.swift [name, isDirty]; platform/ios/plain_rtf/EditorView.swift [EditorView] -->

### Copy, move, or undo text

1. Select the text you want to copy or move.
1. Press **Ctrl+C** to copy it, or **Ctrl+X** to cut it.
1. Place the cursor at the destination and press **Ctrl+V**.
1. To undo a text edit, press **Ctrl+Z**. To redo it, press **Ctrl+Y**.

Undo history lasts for the current document session and is cleared when you
create or open a document. On Windows, undo covers text edits only; to reverse
a formatting change, use the corresponding **Format** command.
<!-- Verified from: platform/windows/plain_rtf/gui/views/root_window.py [_build_editor, _load_document, _handle_paste]; platform/windows/plain_rtf/gui/views/text_buffer.py [_apply_style] -->

On Android, use the menu that appears when you select text to cut, copy, and
paste, and the **Undo** and **Redo** toolbar buttons. Undo there also reverses
formatting changes. With a hardware keyboard, **Ctrl+Z** and **Ctrl+Y** work
as well.
<!-- Verified from: platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/editor/RichEditText.kt [onTextContextMenuItem, onKeyShortcut]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/editor/EditorController.kt [command, undo, redo]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/editor/FormatToolbar.kt [FormatToolbar] -->

On iOS, use the menu that appears when you select text to cut, copy, and
paste. There are no **Undo** or **Redo** buttons; the iPhone's standard undo,
such as shaking the device, works in the text area.
<!-- Verified from: platform/ios/plain_rtf/RichTextEditor.swift [makeUIView]; platform/ios/plain_rtf/FormatToolbar.swift [FormatToolbar] -->

### Open a saved document

1. Choose **File > Open...**, or press **Ctrl+O**.
1. Resolve any unsaved-changes prompt.
1. In **Open document**, choose a Plain Text RTF file. The **RTF documents**
   filter shows `.rtf` files; **All files** lets you select other filenames.
1. Open the file and check the document and the **Opened filename** message.

The file must contain valid Plain Text RTF regardless of its extension.
Canceling the file dialog leaves the current document open. An **Open failed**
dialog also leaves the current document in place. A successful open replaces
the text and clears the previous document's undo history.
<!-- Verified from: platform/windows/plain_rtf/gui/views/root_window.py [_open_file, _open_path, _load_document]; platform/windows/plain_rtf/adapters/files.py [read_rtf] -->

On Android, tap **Open Existing** on the Home screen and choose the file in
Android's file picker. To open another document while one is open, tap
**Back** first. A file that cannot be opened shows **Open failed**.
<!-- Verified from: platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/home/HomeScreen.kt [HomeScreen]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/AppViewModel.kt [open, openDocument, runBusy]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/adapters/DocumentFiles.kt [readText] -->

On iOS, tap **Open Existing** on the Home screen and choose the file in the
file browser, which lists `.rtf` files. To open another document while one is
open, tap **Back** first. A file that cannot be opened shows **Open Failed**
with the reason.
<!-- Verified from: platform/ios/plain_rtf/HomeView.swift [HomeView]; platform/ios/plain_rtf/RTFDocument.swift [init(fileURL:draftStore:)]; platform/ios/plain_rtf/SaveProtection.swift [RTFSerialization] -->

### Save your changes

1. Choose **File > Save**, or press **Ctrl+S**.
1. For an untitled document, choose a folder and filename in **Save document**.
   The default extension is `.rtf`.
1. Complete the dialog and check for **Saved filename** in the status bar.

Saving an existing document writes over its current file. On Windows, a
successful save removes the leading `*` from the title. The document's file
changes only when you request a save. On Windows there is no automatic saving
or recovery copy.
<!-- Verified from: platform/windows/plain_rtf/gui/views/root_window.py [_save_document, _save_document_as, _set_saved_state]; platform/windows/plain_rtf/adapters/files.py [write_rtf] -->

On Android, tap **Save** in the top bar. For a new document, or after you
change the name in the top bar, Android's file picker asks where to save. The
status line then reads **Saved** and the document name. Unsaved changes are
also kept in a recovery draft on the device; see
[Recover unsaved changes](#recover-unsaved-changes).
<!-- Verified from: platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/editor/EditorScreen.kt [EditorScreen]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/AppViewModel.kt [save, write]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/PlainRtfApp.kt [PlainRtfApp]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/domain/session/DocumentSession.kt [scheduleDraftWrite, persistDraft]; platform/android/app/src/main/res/values/strings.xml [status_saved, help_recovery_body] -->

On iOS, tap **Save** in the top bar. For a new document, or after you rename
it, iOS asks where to save and suggests the document's name with `.rtf`.
**Unsaved** disappears once the save succeeds; if it fails, **Save Failed**
gives the reason. Unsaved changes are also kept in a recovery draft.
<!-- Verified from: platform/ios/plain_rtf/EditorView.swift [EditorView, saveToExistingFile]; platform/ios/plain_rtf/RTFDocument.swift [save, markSaved, persistDraft] -->

### Recover unsaved changes

While you edit, the Android and iOS apps keep your unsaved changes in a
recovery draft on the device. The draft is removed once you save or discard
the changes.

1. Open the Home screen and find the document under **Recovery drafts**. On
   iOS, the drafts are listed without a heading.
1. Tap **Recover** beside its name. On iOS, tap **Recover:** followed by its
   name.
1. Review the document, then tap **Save**.

A recovered document counts as unsaved until you save it. If its original file
can no longer be written, **Save** asks where to save. On Android, to remove a
draft without opening it, tap the delete icon beside it and choose **Delete**
in **Delete this draft?**. On iOS, recover the draft, tap **Back**, and choose
**Discard Changes**. Either way, that removes the unsaved changes for good, but
not a file you saved earlier.
<!-- Verified from: platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/home/HomeScreen.kt [HomeScreen, DraftRow]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/AppViewModel.kt [recover, recoverDraft, deleteDraft]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/domain/session/DocumentSession.kt [recovered, persistDraft, discardDraft]; platform/android/app/src/main/res/values/strings.xml [recovery_drafts, action_recover, delete_draft_title, delete_draft_message, help_recovery_body]; platform/ios/plain_rtf/HomeView.swift [HomeView]; platform/ios/plain_rtf/RTFDocument.swift [init(recovering:draftStore:), discardDraft]; platform/ios/plain_rtf/EditorView.swift [EditorView] -->

### Save under a different name or folder

1. Choose **File > Save As...**, or press **Ctrl+Shift+S**.
1. Select the destination folder and enter the new filename.
1. Save and check the new filename in the window title.

Subsequent **Save** commands use the new path. Choose a different filename to
keep the original file. Writing to an existing destination replaces its
contents. Canceling makes no change; if saving fails, the previous document
path remains active.
<!-- Verified from: platform/windows/plain_rtf/gui/views/root_window.py [_save_document_as, _save_document]; platform/windows/plain_rtf/adapters/files.py [write_rtf] -->

On Android, tap **More options**, then **Save As…**, and choose the
destination in Android's file picker.
<!-- Verified from: platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/editor/EditorScreen.kt [OverflowMenu]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/AppViewModel.kt [save, onSaveLocationChosen] -->

iOS has no **Save As** command. Rename the document at the top, then tap
**Save**; iOS asks where to save the copy, and the original file is left as it
was.
<!-- Verified from: platform/ios/plain_rtf/EditorView.swift [EditorView, renameFile] -->

### Apply or remove inline formatting

1. Select the text you want to change.
1. Choose **Format > Bold**, **Italic**, **Underline**, or **Strikethrough**.
   The first three also have **Ctrl+B**, **Ctrl+I**, and **Ctrl+U** shortcuts.
1. Review the selected text and save when ready.

If all selected text already has that style, the command removes it.
Otherwise, it applies the style to the entire selection. Other formatting
remains in place. On Windows, with no text selected, the status reads
**Select text to format it**, and the command makes no change.
<!-- Verified from: platform/windows/plain_rtf/gui/menus/format.py [build_format_menu]; platform/windows/plain_rtf/gui/views/root_window.py [_toggle_style, _bind_shortcuts]; platform/windows/plain_rtf/gui/views/text_buffer.py [toggle_selection_style] -->

On Android, tap the **Bold**, **Italic**, **Underline**, or **Strikethrough**
toolbar button. With nothing selected, the formatting applies to what you type
next.
<!-- Verified from: platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/editor/FormatToolbar.kt [FormatToolbar]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/editor/RichEditText.kt [toggleSelection, transformSelection]; platform/android/app/src/main/res/values/strings.xml [help_editing_body] -->

On iOS, tap the **Bold**, **Italic**, or **Underline** toolbar button. With
nothing selected, the formatting applies to what you type next. Each part of a
mixed selection switches on its own: bold text becomes regular and regular
text becomes bold. iOS has no **Strikethrough** button, but strikethrough
already in a document is kept when you save.
<!-- Verified from: platform/ios/plain_rtf/FormatToolbar.swift [applyTrait, toggleUnderline]; platform/ios/plain_rtf/PlainTextRTFText.swift [attributes(for:), style(from:)] -->

### Change the font, size, or colors

1. Select the text to change.

1. Choose the appropriate **Format** submenu on Windows, or the toolbar button
   with the same name on Android, and then a value:

   | Submenu or button | Choices on Windows | Choices on Android |
   | --- | --- | --- |
   | **Font** | **Automatic**, followed by the font families available on your computer. | **Automatic**, **Sans serif (Arial)**, **Serif (Times New Roman)**, **Monospace (Courier New)**. |
   | **Font Size** | **Automatic**, **10 pt**, **11 pt**, **12 pt**, **14 pt**, **18 pt**. | The same, plus **24 pt** and **36 pt**. |
   | **Text Color** | **Automatic**, **Black**, **Red**, **Green**, **Blue**. | The same. |
   | **Background Color** | **Automatic**, **Yellow**, **Green**, **Blue**. | The same. |

1. Review the selection. To reset that particular attribute, choose
   **Automatic** in the same submenu.

On Windows, automatic font and size are Segoe UI and 11 pt. Automatic colors
remove the explicit color or highlight and use the editor's defaults. These
commands affect selected text immediately and preserve its other formatting.
On Windows, they do not set a formatting preference for future typing with no
selection. On Android, with nothing selected, the choice applies to what you
type next.
<!-- Verified from: platform/windows/plain_rtf/gui/menus/format.py [build_format_menu]; platform/windows/plain_rtf/gui/views/root_window.py [_set_font_family, _set_font_size, _set_text_color, _set_background_color]; platform/windows/plain_rtf/gui/views/text_buffer.py [apply_selection_font_family, apply_selection_font_size, _apply_selection_color_component]; platform/windows/plain_rtf/domains/documents/models.py [DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/editor/FormatToolbar.kt [FONT_CHOICES, FONT_SIZES, TEXT_COLORS, BACKGROUND_COLORS]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/editor/RichEditText.kt [transformSelection]; platform/android/app/src/main/res/values/strings.xml [font_sans, font_serif, font_mono] -->

Android does not have the fonts of a Windows computer. A document that names
another font is shown there in a system font, and the saved font name does not
change.
<!-- Verified from: platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/editor/TextAppearance.kt [genericFamily]; platform/android/app/src/main/res/values/strings.xml [help_editing_body] -->

On iOS, select the text and tap **Font Size** or **Text Color** on the toolbar.
With nothing selected, the choice applies to what you type next.

| Button | Choices on iOS |
| --- | --- |
| **Font Size** | **12 pt**, **14 pt**, **16 pt**, **18 pt**, **20 pt**, **24 pt**, **28 pt**, **32 pt**, **36 pt**, **48 pt**. |
| **Text Color** | **Default**, **Red**, **Blue**, **Green**, **Orange**, **Purple**. |

**Default** resets the text color. The automatic font and size on iOS are the
iPhone's system font at 16 pt. iOS has no **Font** or **Background Color**
button, but fonts and highlights already in a document are kept when you save.
A font the iPhone does not have is shown in the system font, and its saved
name does not change.
<!-- Verified from: platform/ios/plain_rtf/FormatToolbar.swift [FormatToolbar, applyFontSize, applyColor]; platform/ios/plain_rtf/PlainTextRTFText.swift [defaultFontSize, font(for:), style(from:)] -->

### Create, continue, or remove a list

1. Put the cursor on a line, or select several lines.
1. Choose **Format > Bullet List** or **Format > Numbered List**. On Android,
   tap the **Bullet list** or **Numbered list** toolbar button. On iOS, tap
   **Lists**, then **Bullet List** or **Numbered List**.
1. Type an item, then press **Enter** at its end to continue the list.
1. Press **Enter** on an empty list item to remove that marker and end the list.

Applying a list replaces existing bullet or number markers on the affected
lines. Newly applied numbering begins at `1.`. If every affected line already
uses the chosen kind of list, selecting that command removes its markers.
Selecting through the start of the next line excludes that next line.
<!-- Verified from: platform/windows/plain_rtf/gui/views/text_buffer.py [_get_affected_lines, toggle_bullet_list, toggle_numbered_list, handle_return_in_list]; platform/windows/plain_rtf/gui/views/root_window.py [_toggle_bullet_list, _toggle_numbered_list, _handle_return]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/domain/editing/TextCommands.kt [affectedLines, toggleBulletList, toggleNumberedList, continueListAfterNewline]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/editor/FormatToolbar.kt [FormatToolbar] -->

Lists are ordinary text prefixes. Automatic continuation recognizes `•`, `·`,
`-`, or `*`, or a number followed by `.` or `)`, followed by a space or tab at
the beginning of the line. Continuing a numbered item increases its number by
one. Renumbering later lines after edits is not automatic.
<!-- Verified from: platform/windows/plain_rtf/gui/views/text_buffer.py [_BULLET_RE, _NUMBER_RE, handle_return_in_list] -->

On iOS, the list commands start each line with `•` or a number and a period,
followed by a tab, and indent the wrapped text. Pressing **Return** does not
continue a list there, and applying a list adds its marker without replacing
another kind. To extend a list, type the marker yourself, or select the lines
and apply the list again. The indent is restored when you reopen the document.
<!-- Verified from: platform/ios/plain_rtf/FormatToolbar.swift [toggleBulletList, toggleNumberedList, setListIndent]; platform/ios/plain_rtf/PlainTextRTFText.swift [applyListIndents] -->

### Insert and edit a simple table

1. Put the cursor where the table should begin.
1. Choose **Format > Insert Table**. On Android, tap the **Insert table**
   toolbar button.
1. Replace **Column 1**, **Column 2**, and the two **Cell** placeholders.
1. Keep tabs between columns and line breaks between rows. Add or remove text
   as you would elsewhere in the document.

The command inserts a two-column, two-row text template. If the cursor is
mid-line, the table starts on a new line. The cursor moves to the first header.
This is tab-separated text, with no separate cell or table-properties dialog.
<!-- Verified from: platform/windows/plain_rtf/gui/menus/format.py [build_format_menu]; platform/windows/plain_rtf/gui/views/text_buffer.py [insert_table]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/domain/editing/TextCommands.kt [TABLE_TEMPLATE, insertTable] -->

On Android, the **Insert tab** toolbar button adds a tab, since phone
keyboards have no Tab key. Two or more lines in a row that contain tabs are
shown there as a table with a grid around the cells. The grid and column
widths come from the editor and are not saved in the file.
<!-- Verified from: platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/editor/RichEditText.kt [insertTab, drawTableGrids]; platform/android/app/src/main/res/values/strings.xml [format_tab, help_editing_body] -->

iOS has no **Insert table** command. Tables in a document open and save
unchanged there, shown as text separated by tabs.
<!-- Verified from: platform/ios/plain_rtf/FormatToolbar.swift [FormatToolbar]; platform/ios/plain_rtf/PlainTextRTF.swift [parse, format] -->

### Insert an image from a file

1. Place the insertion cursor where the image should appear.
1. Choose **Format > Insert Image...**.
1. In **Insert image**, select an image and open it. The **Images** filter
   lists PNG, JPG, JPEG, GIF, BMP, and WebP files.
1. Check the inserted image and **Inserted filename** status, then save.

Canceling the dialog inserts nothing. Unreadable or unsupported images produce
**Insert image failed**. Images wider than the text area are displayed smaller
while preserving their proportions. PNG and JPEG bytes are retained; other
readable formats are converted to PNG for storage. Images are embedded in the
document, so reopening it does not require the original image file.
<!-- Verified from: platform/windows/plain_rtf/gui/views/root_window.py [IMAGE_FILE_TYPES, _insert_image]; platform/windows/plain_rtf/gui/views/images.py [insert_image_at, insert_image_bytes_at_cursor]; platform/windows/plain_rtf/domains/documents/images.py [decode_image]; platform/windows/plain_rtf/domains/documents/plain_text_rtf.py [_format_image] -->

On Android, tap the **Insert image** toolbar button and pick one image in
Android's photo picker. The status line reads **Inserted image**. Other image
formats are converted to PNG or JPEG, and large photos are scaled down to keep
the file small.
<!-- Verified from: platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/editor/EditorScreen.kt [EditorScreen]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/AppViewModel.kt [insertImages]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/adapters/EmbeddedImages.kt [ImageImporter.fromBytes, MAX_PHOTO_EDGE_PX]; platform/android/app/src/main/res/values/strings.xml [format_image, status_inserted_image, help_editing_body] -->

iOS has no **Insert image** command; paste an image instead, as described in
the next task. Images in a document open there, and wide images are shown
smaller while their saved size stays the same.
<!-- Verified from: platform/ios/plain_rtf/FormatToolbar.swift [FormatToolbar]; platform/ios/plain_rtf/PlainTextRTFText.swift [maximumImageWidth, attributedImage] -->

### Paste an image or text

1. Copy text, a bitmap image, or image files to the Windows clipboard.
1. Click in the editor to set the insertion cursor.
1. Press **Ctrl+V** to paste.

A clipboard bitmap is inserted as PNG. When the clipboard contains file paths,
the first readable image is inserted. A successful image paste reports
**Pasted image**. If no usable image is available, ordinary text paste is used.
<!-- Verified from: platform/windows/plain_rtf/gui/views/root_window.py [_build_editor, _handle_paste]; platform/windows/plain_rtf/gui/views/images.py [look_clipboard_image_bytes] -->

On Android, paste from the menu that appears when you tap or select in the
text area. A pasted image is inserted in the document, and pasted text arrives
as plain text without its original formatting.
<!-- Verified from: platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/editor/RichEditText.kt [receiveContent, onTextContextMenuItem] -->

On iOS, paste from the menu that appears when you tap or select in the text
area. A pasted image is inserted in the document and saved as PNG unless it is
already PNG or JPEG. Pasted text keeps its formatting on screen, but saving
keeps only the formatting the document format can hold, such as fonts, sizes,
colors, bold, italic, underline, and strikethrough. A pasted item that is not
an image, such as a file, stops the save with **Save Failed** until you remove
it.
<!-- Verified from: platform/ios/plain_rtf/RichTextEditor.swift [makeUIView]; platform/ios/plain_rtf/PlainTextRTFText.swift [document(from:), style(from:), image(from:attributes:)] -->

### Drop image files into a note

1. Place the insertion cursor at the desired position in your document.
1. Drag one or more image files from Windows File Explorer onto the text area.
1. Review the inserted images and save the document.

Files are inserted at the current insertion cursor. Unreadable or unsupported
files are skipped. If none can be inserted, the status reads
**Dropped file is not a supported image**. Use **File > Open...** to open a
document; dropping files is an image insertion action.
<!-- Verified from: platform/windows/plain_rtf/gui/views/root_window.py [_register_drop_target, _handle_drop]; platform/windows/plain_rtf/gui/views/images.py [insert_image_bytes_at_cursor] -->

On Android, an image dragged into the text area from another app is inserted
in the same way as a pasted image.
<!-- Verified from: platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/editor/RichEditText.kt [receiveContent]; platform/android/app/src/main/res/values/strings.xml [help_editing_body] -->

### Remove an embedded image

1. Select the image's position in the document along with any text you intend
   to remove.
1. Press **Delete**, then review the surrounding text.
1. Save to persist the removal.

Each image occupies one position in the document. Only images still present
in the text area are included when saving.
<!-- Verified from: platform/windows/plain_rtf/gui/views/root_window.py [_build_editor, _save_document]; platform/windows/plain_rtf/gui/views/text_buffer.py [read_document_from_text, _look_image_name_at] -->

### Look up help while working

1. Open **Help**.
1. Choose **Keyboard Shortcuts** for the application shortcuts, **RTF Support**
   for the supported document features, or **About RTF Editor** for a brief
   description.
1. Dismiss the dialog to resume editing.
<!-- Verified from: platform/windows/plain_rtf/gui/menus/help.py [build_help_menu, show_keyboard_shortcuts, show_rtf_support, show_about] -->

On Android, tap the **Help** icon on the Home screen, or **More options** and
then **Help** in the editor. One screen holds **About Plain RTF**,
**Document format**, **Editing**, **Saving and recovery**, **Feedback**, and
**Keyboard shortcuts**. Tap **Back** to return. The **Privacy** icon on the
Home screen shows the app's privacy policy, and its
**Contact Plain Text Office** button opens the contact page on our website.
<!-- Verified from: platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/home/HomeScreen.kt [HomeScreen]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/editor/EditorScreen.kt [OverflowMenu]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/info/InfoScreens.kt [HELP_SECTIONS, HelpScreen, PrivacyScreen, CONTACT_URL]; platform/android/app/src/main/res/values/strings.xml -->

The iOS app has no help screen; use this manual. **Privacy** on the Home
screen shows the app's privacy policy, and its **Contact Plain Text Office**
link opens the contact page on our website.
<!-- Verified from: platform/ios/plain_rtf/HomeView.swift [HomeView]; platform/ios/plain_rtf/PrivacyPolicyView.swift [PrivacyPolicyButton, PrivacyPolicyView] -->

## Settings and Preferences

Not Applicable.

There is no user preferences dialog or user-editable settings file. The
**Format** choices described above change document content, take effect
immediately, and persist in that document when saved. They are not global
preferences for later documents or sessions.
<!-- Verified from: platform/windows/plain_rtf/gui/menus/menu.py [build_menu_bar]; platform/windows/plain_rtf/gui/menus/format.py [build_format_menu]; platform/windows/plain_rtf/gui/views/root_window.py [__init__, _save_document]; platform/windows/plain_rtf/domains/documents/plain_text_rtf.py [_format_style_attributes] -->

## Importing and Exporting

Use **File > Open...**, **Save**, and **Save As...** for native documents.
There is no separate import/export command or conversion to Microsoft RTF,
DOCX, PDF, or HTML. Plain text files without the required header do not open
as documents; paste their text into a new note instead.
<!-- Verified from: platform/windows/plain_rtf/gui/menus/file.py [build_file_menu]; platform/windows/plain_rtf/gui/views/root_window.py [_open_file, _save_document, _save_document_as, _handle_paste]; platform/windows/plain_rtf/domains/documents/plain_text_rtf.py [parse_plain_text_rtf] -->

| Input or output | How to use it | Rules |
| --- | --- | --- |
| Plain Text RTF | Open with **File > Open...**; write with **Save** or **Save As...**. | UTF-8, `PTRTF/1` header, valid markers; normally `.rtf`. |
| Image files | Insert, paste, or drop them using the tasks above. | Must decode as an image; stored inside the document as PNG or JPEG. |
| Clipboard text | Paste into the document. | Ordinary text paste is used when the clipboard supplies no usable image. |
<!-- Verified from: platform/windows/plain_rtf/adapters/files.py [read_rtf, write_rtf]; platform/windows/plain_rtf/gui/views/root_window.py [_insert_image, _handle_paste, _handle_drop]; platform/windows/plain_rtf/domains/documents/images.py [decode_image] -->

The destination is the path you select in **Save document**, not an automatic
export folder. Repeated image insertions add more images; they do not replace
earlier copies. Saving overwrites the destination file. For the native file
layout and a complete text example, see [Your Data Files](#your-data-files).
<!-- Verified from: platform/windows/plain_rtf/gui/views/root_window.py [_save_document_as]; platform/windows/plain_rtf/gui/views/images.py [insert_image_at]; platform/windows/plain_rtf/adapters/files.py [write_rtf] -->

On iOS, use **Open Existing** and **Save** for native documents, and paste to
bring in images or text. The iOS app reads and writes the same Plain Text RTF
files as the other apps, so documents can move between them.
<!-- Verified from: platform/ios/plain_rtf/HomeView.swift [HomeView]; platform/ios/plain_rtf/EditorView.swift [EditorView]; platform/ios/plain_rtf/PlainTextRTF.swift [parse, format] -->

## Commands and Shortcuts

### Launch from a Windows terminal

Run the command from the folder that holds `plain-rtf.exe`.

| Command or argument | Accepted values | What it does |
| --- | --- | --- |
| `./plain-rtf.exe` | Optional document path. | Opens the desktop editor. |
| First argument | An existing Plain Text RTF file path; quote spaces. | Opens that document at startup. |
| Additional arguments | Ignored. | No additional action. |
<!-- Verified from: platform/windows/pyproject.toml [executable-name]; platform/windows/plain_rtf/main.py [_get_startup_path, main] -->

No named command-line options are defined. For example, `--help` would be
treated as a filename; use the **Help** menu for assistance.
<!-- Verified from: platform/windows/plain_rtf/main.py [_get_startup_path]; platform/windows/plain_rtf/gui/menus/help.py [build_help_menu] -->

### Use Windows menus and keys

| Menu | Command | Shortcut | What it does |
| --- | --- | --- | --- |
| **File** | **New** | **Ctrl+N** | Replaces the current document with an empty one after any save prompt. |
| **File** | **Open...** | **Ctrl+O** | Opens a native document. |
| **File** | **Save** | **Ctrl+S** | Saves to the current path, asking for one if needed. |
| **File** | **Save As...** | **Ctrl+Shift+S** | Saves to a chosen path and makes it current. |
| **File** | **Exit** | None assigned. | Closes after any save prompt. |
| **Format** | **Bold** | **Ctrl+B** | Toggles bold on the selection. |
| **Format** | **Italic** | **Ctrl+I** | Toggles italics on the selection. |
| **Format** | **Underline** | **Ctrl+U** | Toggles underlining on the selection. |
| **Format** | **Strikethrough** | None assigned. | Toggles strikethrough on the selection. |
| **Format** | **Font**, **Font Size** | None assigned. | Changes the selected text's typeface or point size. |
| **Format** | **Text Color**, **Background Color** | None assigned. | Changes the selected text's color or highlight. |
| **Format** | **Bullet List**, **Numbered List** | None assigned. | Toggles markers on the current or selected lines. |
| **Format** | **Insert Table** | None assigned. | Inserts the tab-separated template. |
| **Format** | **Insert Image...** | None assigned. | Chooses an image file to insert. |
| **Help** | **Keyboard Shortcuts** | None assigned. | Displays the application shortcut list. |
| **Help** | **RTF Support** | None assigned. | Describes the native format and features. |
| **Help** | **About RTF Editor** | None assigned. | Displays the application description. |
<!-- Verified from: platform/windows/plain_rtf/gui/menus/file.py [build_file_menu]; platform/windows/plain_rtf/gui/menus/format.py [build_format_menu]; platform/windows/plain_rtf/gui/menus/help.py [build_help_menu]; platform/windows/plain_rtf/gui/views/root_window.py [_bind_shortcuts] -->

The editing area also supports these Windows text shortcuts:

| Shortcut | Action |
| --- | --- |
| **Ctrl+C** | Copy selected text. |
| **Ctrl+X** | Cut selected text. |
| **Ctrl+V** | Paste an image when available, otherwise text. |
| **Ctrl+Z** | Undo a text edit. |
| **Ctrl+Y** | Redo a text edit. |
<!-- Verified from: platform/windows/plain_rtf/gui/views/root_window.py [_build_editor, _handle_paste] -->

In the editing area, **Enter** continues a list or inserts an ordinary line
break. On an empty list item it removes the marker. **Ctrl+V** uses the image
or text paste behavior described above.
<!-- Verified from: platform/windows/plain_rtf/gui/views/root_window.py [_build_editor, _handle_return, _handle_paste]; platform/windows/plain_rtf/gui/views/text_buffer.py [handle_return_in_list] -->

### Use Android buttons and keys

The Android commands are the top-bar and toolbar buttons listed in
[Getting Around](#getting-around). With a hardware keyboard, these keys also
work in the editor:

| Shortcut | Action |
| --- | --- |
| **Tab** | Insert a tab. |
| **Ctrl+S** | Save. |
| **Ctrl+Shift+S** | Save As. |
| **Ctrl+B** | Toggle bold. |
| **Ctrl+I** | Toggle italics. |
| **Ctrl+U** | Toggle underlining. |
| **Ctrl+Z** | Undo. |
| **Ctrl+Y** or **Ctrl+Shift+Z** | Redo. |
<!-- Verified from: platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/editor/RichEditText.kt [onKeyDown, onKeyShortcut]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/editor/EditorController.kt [onShortcut]; platform/android/app/src/main/res/values/strings.xml [help_shortcuts_body] -->

### Use iOS buttons

The iOS commands are the top-bar and toolbar buttons listed in
[Getting Around](#getting-around). The app defines no keyboard shortcuts of its
own.

| Button | Where | What it does |
| --- | --- | --- |
| **Back** | Editor top bar | Returns to the Home screen, offering to keep or discard unsaved changes. |
| **Save** | Editor top bar | Saves to the current file, or asks where to save a new or renamed document. |
| **Bold**, **Italic**, **Underline** | Format toolbar | Switches the style on the selection or for what you type next. |
| **Font Size**, **Text Color** | Format toolbar | Changes the selected text's size or color. |
| **Lists** | Format toolbar | Adds or removes bullet or number markers on the current or selected lines. |
<!-- Verified from: platform/ios/plain_rtf/EditorView.swift [EditorView]; platform/ios/plain_rtf/FormatToolbar.swift [FormatToolbar] -->

## Your Data Files

### Locate documents and diagnostic logs

| File | Location | Purpose and editing guidance |
| --- | --- | --- |
| Your `.rtf` documents | The folder you choose when saving. | Stores text, formatting, and embedded images. May be edited as UTF-8 text using the rules below. |
| Original image files | Wherever you selected them. | Read when inserted; the document stores its own image content. |
| `logs/rtf-editor.log` | Windows only: under `plain-rtf-data/` beside a portable executable; under `%LOCALAPPDATA%/plain-rtf/` for an installed application. | Diagnostic output. Read it when investigating problems; it is not a document or preferences file. |
| `logs/rtf-editor.1.log` through `logs/rtf-editor.3.log` | Beside the main log. | Older diagnostic output retained as the log rotates at approximately 1,000,000 bytes. |
| Recovery drafts | Android and iOS: the app's own storage on the device. | Hold unsaved changes until you save or discard them. Manage them from the Home screen, not by hand. |
<!-- Verified from: platform/windows/plain_rtf/adapters/files.py [read_rtf, write_rtf]; platform/windows/plain_rtf/gui/views/root_window.py [_save_document_as]; platform/windows/plain_rtf/domains/documents/plain_text_rtf.py [_format_image]; platform/windows/plain_rtf/gui/app.py [launch_app]; platform/windows/plain_rtf/config/path_handler.py [LOGS_DIR, APP_ROOT]; platform/windows/plain_rtf/config/logging/log_config.py [configure_logging, _rotating_handler_factory]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/AppViewModel.kt [Factory]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/domain/session/DraftStore.kt -->

On Android, you choose where each document is saved in Android's file picker.
A file stored with a provider such as Google Drive or Dropbox may be uploaded
or synchronized by that provider. Recovery drafts are left out of Android
device backups and transfers, and uninstalling the app removes them. Documents
you saved are separate and stay where they are.
<!-- Verified from: platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/PlainRtfApp.kt [PlainRtfApp]; platform/android/app/src/main/AndroidManifest.xml [allowBackup]; platform/android/app/src/main/res/xml/backup_rules.xml; platform/android/app/src/main/res/xml/data_extraction_rules.xml; platform/android/app/src/main/res/values/strings.xml [privacy_saving_body, privacy_removing_body] -->

On iOS, you choose where each document is saved in the file browser. A file in
iCloud Drive or with another provider may be uploaded or synchronized by that
provider. Recovery drafts are kept in the app's own storage, which is included
in iPhone backups, and deleting the app removes them. Documents you saved are
separate and stay where they are.
<!-- Verified from: platform/ios/plain_rtf/EditorView.swift [EditorView]; platform/ios/plain_rtf/SaveProtection.swift [DraftStore.standard]; platform/ios/plain_rtf/PrivacyPolicyView.swift [PrivacyPolicyView] -->

The Windows portable executable needs a writable folder. Its application data
stays beside it and is not redirected to AppData if that folder cannot be
written. If **Cannot write application data** appears, move the executable to a
writable folder and try again. Your documents still use the paths you select
when saving. The portable data folder follows the executable's name:
`My Notes.exe` uses `My Notes-data/`. Rename its existing data folder too if you
want to retain the logs when renaming the executable.
<!-- Verified from: platform/windows/plain_rtf/config/path_handler.py [STORAGE_MODE, ROOT_DIR]; platform/windows/plain_rtf/gui/app.py [_show_storage_error]; platform/windows/plain_rtf/gui/views/root_window.py [_save_document_as] -->

Use **Save As...** to change a document's storage location. Save or close the
document before editing its file elsewhere, then reopen it to load those
changes. An already-open document does not refresh from external edits, and
its next save writes its current contents over the file.
<!-- Verified from: platform/windows/plain_rtf/gui/views/root_window.py [_open_path, _save_document, _save_document_as]; platform/windows/plain_rtf/adapters/files.py [write_rtf] -->

### Read or edit a native document by hand

1. Open a saved document in a text editor that supports UTF-8.
1. Keep `PTRTF/1` as the exact first line, with no leading spaces.
1. Edit the body using ordinary text and, if needed, the markers below.
1. Save as UTF-8, then open the file in RTF Editor to check it.

This is a complete valid example:

```text
PTRTF/1
Meeting notes
[[bold=true]]Decisions[[/]]
• Confirm the date.
• Share the agenda.
[[font=Segoe%20UI;size=14;color=#ff0000]]Follow up tomorrow.[[/]]
```
<!-- Verified from: platform/windows/plain_rtf/adapters/files.py [read_rtf, write_rtf]; platform/windows/plain_rtf/domains/documents/plain_text_rtf.py [parse_plain_text_rtf, _read_attributes, _read_style, _BodyReader] -->

A style starts with `[[name=value]]` and ends with `[[/]]`. Combine attributes
inside the opening marker using semicolons. Do not nest style spans. Line
breaks and tabs in the body remain line breaks and tabs in the document.
<!-- Verified from: platform/windows/plain_rtf/domains/documents/plain_text_rtf.py [_read_attributes, _BodyReader, parse_plain_text_rtf] -->

| Attribute | Accepted value | Default when omitted or invalid |
| --- | --- | --- |
| `font` | A percent-encoded family name, such as `Segoe%20UI`. | Segoe UI. |
| `size` | Positive integer points, such as `14`. | 11 pt. |
| `color` | Lowercase hex color, such as `#ff0000`. | Automatic text color. |
| `background` | Lowercase hex color, such as `#fff59d`. | No explicit highlight. |
| `bold`, `italic`, `underline`, `strikethrough` | `true` enables the attribute; `false` disables it. | Disabled; only exact `true` enables it. |
<!-- Verified from: platform/windows/plain_rtf/domains/documents/plain_text_rtf.py [_read_style, _look_positive_integer, _look_color, _look_font_family, _look_enabled]; platform/windows/plain_rtf/domains/documents/models.py [DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE] -->

Attribute names must contain lowercase letters and cannot repeat within a
marker. Unknown attributes are ignored. Unavailable fonts retain their saved
names; their on-screen appearance depends on font availability on the computer.
<!-- Verified from: platform/windows/plain_rtf/domains/documents/plain_text_rtf.py [_read_attributes, _read_style, _format_style_attributes]; platform/windows/plain_rtf/gui/views/text_buffer.py [_ensure_style_tag, _look_style] -->

Escape literal markup characters in text as follows:

| Character wanted | Write in the file |
| --- | --- |
| `[` | `\[` |
| `]` | `\]` |
| `\` | `\\` |
<!-- Verified from: platform/windows/plain_rtf/domains/documents/plain_text_rtf.py [_escape_text, _read_escape] -->

Embedded images have a single marker with these required attributes and no
closing `[[/]]`:

| Attribute | Required content |
| --- | --- |
| `image` | `png` or `jpeg`, matching the actual image bytes. |
| `width` | Positive integer display width in pixels. |
| `height` | Positive integer display height in pixels. |
| `payload` | Complete standard Base64 image bytes on one unwrapped line. |

Use the editor's image insertion commands to produce these markers. Invalid
image dimensions, unsupported formats, invalid Base64, or a payload that does
not match its declared format prevent the document from opening. Saved image
bytes are contained in the file, not referenced by a separate filename.
<!-- Verified from: platform/windows/plain_rtf/domains/documents/plain_text_rtf.py [_format_image, _read_image] -->

## Troubleshooting

| Symptom | Likely Cause | Resolution |
| --- | --- | --- |
| **Open failed** says **This file is not a Plain Text RTF document.** | The first line is not exactly `PTRTF/1`, or the file uses another format. | Open a native document. For ordinary text, paste into a new note; renaming a Microsoft RTF file does not convert it. |
| **Open failed** reports an unclosed marker, unclosed style span, or nested style spans. | Hand-edited markup is incomplete or nested. | Correct the file using the native-format rules above and reopen it. |
| **Open failed** reports invalid image data or a format mismatch. | An embedded image marker or payload is invalid. | Correct the image marker or remove it in a text editor, then reinsert the original image through **Insert Image...**. |
| **Open failed** reports a file access or decoding error. | The path cannot be read, or the file is not UTF-8. | Choose a readable native document and ensure hand-edited files are saved as UTF-8. The current document remains open. |
<!-- Verified from: platform/windows/plain_rtf/gui/views/root_window.py [_open_path]; platform/windows/plain_rtf/adapters/files.py [read_rtf]; platform/windows/plain_rtf/domains/documents/plain_text_rtf.py [parse_plain_text_rtf, _BodyReader, _read_image] -->

| Symptom | Likely Cause | Resolution |
| --- | --- | --- |
| **Save failed** | The selected destination cannot be written. | Read the error, then use **Save As...** to select an existing writable folder. Unsaved changes remain in the editor. |
| **Select text to format it**, **Select text to change its font**, **Select text to resize it**, or **Select text to color it** | No text is selected. | Select the text and repeat the command. |
| **Insert image failed** | The selected file is unreadable or cannot be decoded as an image. | Choose a readable supported image file. |
| **Dropped file is not a supported image** | None of the dropped files could be inserted as images. | Drop readable images; use **File > Open...** for documents. |
| Pasting copied files inserts only one image. | Clipboard file paste selects the first readable image. | Drop multiple files onto the editor to insert several images. |
| A list keeps adding markers when you press **Enter**. | The current line is a recognized list item. | Press **Enter** on an empty list item, or toggle the matching list command to remove markers. |
| A wide image appears smaller. | Image display is reduced to fit the text area. | This is expected; PNG and JPEG source bytes are preserved in the document. |
| On Android, **Send feedback** reports that no email app is set up on this device. | Feedback is sent through your own email app. | Write to the address shown from any other device. |
| On iOS, **Send Feedback** reports that no email app is set up on this device. | Feedback is sent through your own email app. | Tap **Open contact form** and write from the browser. |
| On iOS, **Save Failed** says the document contains an attachment that is not an image. | Something other than an image, such as a file, was pasted into the document. | Delete that item and save again. Your unsaved changes stay in the recovery draft. |
| On iOS, an alert reads **Open Failed** instead of **Open failed**. | iOS capitalizes the title; the messages are the same. | Use the **Open failed** rows in the first table. |
<!-- Verified from: platform/windows/plain_rtf/gui/views/root_window.py [_save_document, _set_font_family, _set_font_size, _set_text_color, _set_background_color, _toggle_style, _insert_image, _handle_drop]; platform/windows/plain_rtf/gui/views/images.py [look_clipboard_image_bytes, insert_image_at]; platform/windows/plain_rtf/gui/views/text_buffer.py [handle_return_in_list]; platform/windows/plain_rtf/domains/documents/images.py [decode_image]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/info/InfoScreens.kt [FeedbackScreen]; platform/android/app/src/main/res/values/strings.xml [feedback_no_email_app]; platform/ios/plain_rtf/Feedback.swift [FeedbackView]; platform/ios/plain_rtf/PlainTextRTFText.swift [image(from:attributes:)]; platform/ios/plain_rtf/HomeView.swift [HomeView]; platform/ios/plain_rtf/PlainTextRTF.swift [PlainTextRTFError] -->

For file errors, use the dialog's message first. The Windows diagnostic log
location is listed above, but open/save errors are shown in dialogs and are
not explicitly written to that log.
<!-- Verified from: platform/windows/plain_rtf/gui/views/root_window.py [_open_path, _save_document]; platform/windows/plain_rtf/config/logging/log_config.py [configure_logging] -->

## FAQ

### Can I open Microsoft Word RTF files?

No. The native format requires the `PTRTF/1` header and has its own formatting
markers. The `.rtf` extension alone does not establish compatibility.
<!-- Verified from: platform/windows/plain_rtf/gui/menus/help.py [RTF_SUPPORT_TEXT]; platform/windows/plain_rtf/domains/documents/plain_text_rtf.py [parse_plain_text_rtf] -->

### Does the editor save automatically?

Not to the document's file. Use **Save** or **Save As...**. On Windows, New,
Open, and Exit prompt when there are unsaved changes; **Cancel** lets you
return to the current document. There is no recovery copy on Windows.
<!-- Verified from: platform/windows/plain_rtf/gui/views/root_window.py [_save_document, _new_file, _open_file, _on_close, _prompt_for_unsaved_changes] -->

On Android, unsaved changes are also kept in a recovery draft on the device
until you save or discard them, and the Home screen lists the drafts you can
recover or delete.
<!-- Verified from: platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/domain/session/DocumentSession.kt [scheduleDraftWrite, persistDraft]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/home/HomeScreen.kt [HomeScreen]; platform/android/app/src/main/res/values/strings.xml [help_recovery_body] -->

On iOS, unsaved changes are kept in a recovery draft in the same way, and the
Home screen lists the drafts you can recover.
<!-- Verified from: platform/ios/plain_rtf/RTFDocument.swift [schedulePersistDraft, persistDraft]; platform/ios/plain_rtf/HomeView.swift [HomeView] -->

### Do I need to send image files with my document?

No. Inserted images are embedded in the saved document as PNG or JPEG data.
<!-- Verified from: platform/windows/plain_rtf/domains/documents/plain_text_rtf.py [_format_image, _read_image] -->

### Can I choose a custom font size or color?

The menus offer the sizes and colors listed above. Hand-edited native files
can specify other positive integer point sizes and lowercase `#rrggbb`
colors. There is no custom size entry field or color picker in the menus.
<!-- Verified from: platform/windows/plain_rtf/gui/menus/format.py [build_format_menu]; platform/windows/plain_rtf/domains/documents/plain_text_rtf.py [_look_positive_integer, _look_color] -->

### Why does changing bold affect the whole selection?

The command enables bold across the selection unless every selected character
is already bold, in which case it removes bold. Italic, underline, and
strikethrough follow the same rule. On iOS, each part of a mixed selection
switches on its own instead.
<!-- Verified from: platform/windows/plain_rtf/gui/views/text_buffer.py [toggle_selection_style]; platform/ios/plain_rtf/FormatToolbar.swift [applyTrait, toggleUnderline] -->

### Are tables and lists special document objects?

No. Tables use tabs and line breaks; lists use visible text prefixes. You can
edit their text directly, and list commands help add or remove the prefixes.
<!-- Verified from: platform/windows/plain_rtf/gui/views/text_buffer.py [insert_table, toggle_bullet_list, toggle_numbered_list] -->

## Feedback

Send bug reports and feature requests to
[support@plaintxtoffice.com](mailto:support@plaintxtoffice.com) or through the
[contact page](https://plaintxtoffice.com/contact/) from any device. The
Android and iOS apps also have a feedback screen.

| Platform | How to open feedback |
| --- | --- |
| Windows | Version 0.1.0 has no feedback command. **Help > Send Feedback...** is in development for the next Windows release. |
| Android | Tap the **Send feedback** icon on the Home screen, or **More options** and then **Send feedback** in the editor. |
| iOS | Tap **Send Feedback** at the top of the Home screen. |
<!-- Verified from: https://github.com/PlainTxtOffice/plain-rtf/releases [v0.1.0, 2026-11-10]; platform/windows/plain_rtf/gui/menus/help.py [build_help_menu]; platform/windows/plain_rtf/gui/feedback.py; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/home/HomeScreen.kt [HomeScreen]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/editor/EditorScreen.kt [OverflowMenu]; platform/ios/plain_rtf/HomeView.swift [HomeView] -->

### Send feedback on Windows (in development)

The Windows release available now, version 0.1.0, has no feedback command;
write to `support@plaintxtoffice.com` or use the
[contact form](https://plaintxtoffice.com/contact/). The next Windows release
adds a feedback dialog:

1. Choose **Help > Send Feedback...**.
1. Click **Report a Bug** or **Request a Feature**. Your email app opens a
   message to `support@plaintxtoffice.com` with the app version and your
   Windows version filled in; your documents are not included.
1. Review or change it, then send it. Nothing is sent unless you send it.
1. To use the website instead, click **Open Contact Form**.
<!-- Verified from: https://github.com/PlainTxtOffice/plain-rtf/releases [v0.1.0]; platform/windows/plain_rtf/gui/menus/help.py [build_help_menu]; platform/windows/plain_rtf/gui/feedback.py -->

### Send feedback on Android

1. Tap the **Send feedback** icon on the Home screen, or **More options** and
   then **Send feedback** in the editor.
1. Tap **Report a bug** or **Request a feature**.
1. Your email app opens a draft email to Plain Text Office that includes the
   app version, your Android version, and your device model. Review or change
   it, then send it.

The app sends nothing itself; the message goes only if you send it. If no
email app is set up, the screen shows the address so that you can write from
another device.
<!-- Verified from: platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/home/HomeScreen.kt [HomeScreen]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/editor/EditorScreen.kt [OverflowMenu]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/info/InfoScreens.kt [FeedbackScreen]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/info/Feedback.kt [FEEDBACK_ADDRESS, draftFeedbackEmail, openFeedbackEmail]; platform/android/app/src/main/res/values/strings.xml [feedback_body, feedback_report_bug, feedback_request_feature, feedback_no_email_app] -->

### Send feedback on iOS

Tap **Send Feedback** at the top of the Home screen. **Report a bug** and
**Request a feature** open a message to `support@plaintxtoffice.com` in
your email app, with the app version, your iOS version, and your device model
filled in; your documents are not included. **Open contact form** opens the
contact page in your browser instead. If no email app is set up, the screen
says so and suggests **Open contact form**. Tap **Done** to close it.
<!-- Verified from: platform/ios/plain_rtf/HomeView.swift [HomeView]; platform/ios/plain_rtf/Feedback.swift [Feedback, FeedbackView] -->

## Glossary

| Term | Meaning |
| --- | --- |
| Plain Text RTF | This editor's UTF-8 document format, identified by `PTRTF/1`. |
| Selection | Text highlighted for replacement, removal, or formatting. |
| Insertion cursor | The position where typing or an inserted image appears. |
| Inline formatting | Font, size, colors, bold, italic, underline, or strikethrough applied to text. |
| Embedded image | Image content stored inside the document file. |
| Marker | A `[[...]]` instruction in the native file that describes styling or an image. |
| Unsaved changes | Edits not yet written to the document's file, indicated by a leading `*` in the title on Windows, by **Unsaved changes** in the status line on Android, and by **Unsaved** at the bottom of the editor on iOS. |
| Recovery draft | The Android or iOS app's copy of a document's unsaved changes, kept on the device until you save or discard them. |
<!-- Verified from: platform/windows/plain_rtf/domains/documents/plain_text_rtf.py [FORMAT_HEADER, _format_styled_text, _format_image]; platform/windows/plain_rtf/gui/views/text_buffer.py [_look_selection_range]; platform/windows/plain_rtf/gui/views/images.py [insert_image_bytes_at_cursor]; platform/windows/plain_rtf/gui/views/root_window.py [_update_title]; platform/android/app/src/main/kotlin/com/plaintxtoffice/plainrtf/ui/editor/EditorScreen.kt [EditorStatusBar]; platform/android/app/src/main/res/values/strings.xml [help_recovery_body] -->
