---
last_updated: 2026-10-21
version: 3.1.0
product_version: "0.1.0"
generated_from: "dev-docs/specs/USER_MANUAL_SPEC.instructions.md"
---

# User Manual

## Overview

Plain RTF, named **RTF Editor** in its window, is a desktop editor for people
writing quick rich-text notes on Windows. It supports text formatting, lists,
simple tables, and embedded images through a graphical interface. Terminal
commands launch that same interface. This manual covers everyday use;
installation and setup are not covered.
<!-- Verified from: pyproject.toml [project]; src/gui/menus/help.py [ABOUT_TEXT]; src/main.py [main] -->

Documents use the application's **Plain Text RTF** format. Although filenames
normally end in `.rtf`, these are UTF-8 text files beginning with `PTRTF/1`.
They are not Microsoft RTF documents and cannot be exchanged as Microsoft RTF.
<!-- Verified from: src/gui/menus/help.py [RTF_SUPPORT_TEXT]; src/domains/documents/plain_text_rtf.py [FORMAT_HEADER, parse_plain_text_rtf] -->

## Starting the Program

From the project folder, run:

```powershell
.venv/Scripts/python.exe -m src.main
```

The installed command is:

```powershell
plain-rtf
```

Both open an empty document titled **Untitled - RTF Editor**. The status bar
shows **New document** and **0 characters**.
<!-- Verified from: pyproject.toml [project.gui-scripts]; src/main.py [main]; src/gui/views/root_window.py [__init__, _update_title, _set_saved_state, _update_char_count] -->

To open an existing document immediately, supply its path as the first
argument. Quote paths containing spaces:

```powershell
.venv/Scripts/python.exe -m src.main "C:/Users/YourName/Documents/My notes.rtf"
plain-rtf "C:/Users/YourName/Documents/My notes.rtf"
```

Use an existing Plain Text RTF file. Relative paths are relative to the folder
from which you launch the command. An unsuccessful startup open shows
**Open failed** and leaves an empty document available.
<!-- Verified from: src/main.py [_get_startup_path]; src/adapters/files.py [read_rtf]; src/gui/views/root_window.py [__init__, _open_path] -->

To quit, choose **File > Exit** or close the window. If prompted to save,
choose **Yes** to save first, **No** to discard unsaved changes, or **Cancel**
to keep working. Canceling the save dialog or failing to save also stops the
close operation.
<!-- Verified from: src/gui/menus/file.py [build_file_menu]; src/gui/views/root_window.py [_on_close, _prompt_for_unsaved_changes, _save_document_as] -->

## Getting Around

The window holds one document at a time. Click in the main text area to place
the insertion cursor, type, or select text. Text wraps at word boundaries;
use the vertical scrollbar to move through a longer document.
<!-- Verified from: src/gui/views/root_window.py [_build_editor, _load_document] -->

| Area | What it tells you or lets you do |
| --- | --- |
| Title bar | Shows the current filename, or **Untitled**. A leading `*` marks unsaved changes. |
| **File** menu | Create, open, save, rename through **Save As...**, or exit. |
| **Format** menu | Format selected text, change list markers, and insert tables or images. |
| **Help** menu | Open **Keyboard Shortcuts**, **RTF Support**, or **About RTF Editor**. |
| Status bar, left | Reports actions and hints, such as **Unsaved changes** or **Opened notes.rtf**. |
| Status bar, right | Counts document characters; each embedded image counts as one. |
<!-- Verified from: src/gui/menus/file.py [build_file_menu]; src/gui/menus/format.py [build_format_menu]; src/gui/menus/help.py [build_help_menu]; src/gui/views/root_window.py [_update_title, _build_status_bar, _update_char_count] -->

## Everyday Tasks

### Create and edit a note

1. Choose **File > New**, or press **Ctrl+N**.
1. Resolve the save prompt if your current document has unsaved changes.
1. Type in the empty text area. Press **Enter** for a new line.
1. Select existing text to replace it by typing, or remove it with **Delete**.
1. Save the note with **File > Save**.

The title begins with `*` after an edit. Starting a new document replaces the
current document and clears its undo history. **Cancel** at the unsaved-changes
prompt keeps the current document open.
<!-- Verified from: src/gui/views/root_window.py [_new_file, _build_editor, _handle_return, _handle_modified, _load_document, _prompt_for_unsaved_changes] -->

### Copy, move, or undo text

1. Select the text you want to copy or move.
1. Press **Ctrl+C** to copy it, or **Ctrl+X** to cut it.
1. Place the cursor at the destination and press **Ctrl+V**.
1. To undo a text edit, press **Ctrl+Z**. To redo it, press **Ctrl+Y**.

Text undo history lasts for the current document session and is cleared when
you create or open a document. To reverse a formatting change, use the
corresponding **Format** command; text undo does not reverse those changes.
<!-- Verified from: src/gui/views/root_window.py [_build_editor, _load_document, _handle_paste]; src/gui/views/text_buffer.py [_apply_style] -->

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
<!-- Verified from: src/gui/views/root_window.py [_open_file, _open_path, _load_document]; src/adapters/files.py [read_rtf] -->

### Save your changes

1. Choose **File > Save**, or press **Ctrl+S**.
1. For an untitled document, choose a folder and filename in **Save document**.
   The default extension is `.rtf`.
1. Complete the dialog and check for **Saved filename** in the status bar.

Saving an existing document writes over its current file. A successful save
removes the leading `*` from the title. Changes are saved when you request a
save; there is no automatic document saving or recovery copy.
<!-- Verified from: src/gui/views/root_window.py [_save_document, _save_document_as, _set_saved_state]; src/adapters/files.py [write_rtf] -->

### Save under a different name or folder

1. Choose **File > Save As...**, or press **Ctrl+Shift+S**.
1. Select the destination folder and enter the new filename.
1. Save and check the new filename in the window title.

Subsequent **Save** commands use the new path. Choose a different filename to
keep the original file. Writing to an existing destination replaces its
contents. Canceling makes no change; if saving fails, the previous document
path remains active.
<!-- Verified from: src/gui/views/root_window.py [_save_document_as, _save_document]; src/adapters/files.py [write_rtf] -->

### Apply or remove inline formatting

1. Select the text you want to change.
1. Choose **Format > Bold**, **Italic**, **Underline**, or **Strikethrough**.
   The first three also have **Ctrl+B**, **Ctrl+I**, and **Ctrl+U** shortcuts.
1. Review the selected text and save when ready.

If all selected text already has that style, the command removes it.
Otherwise, it applies the style to the entire selection. Other formatting
remains in place. With no text selected, the status reads
**Select text to format it**, and the command makes no change.
<!-- Verified from: src/gui/menus/format.py [build_format_menu]; src/gui/views/root_window.py [_toggle_style, _bind_shortcuts]; src/gui/views/text_buffer.py [toggle_selection_style] -->

### Change the font, size, or colors

1. Select the text to change.
1. Choose the appropriate **Format** submenu and then a value:

   | Submenu | Available choices |
   | --- | --- |
   | **Font** | **Automatic**, followed by the font families available on your computer. |
   | **Font Size** | **Automatic**, **10 pt**, **11 pt**, **12 pt**, **14 pt**, **18 pt**. |
   | **Text Color** | **Automatic**, **Black**, **Red**, **Green**, **Blue**. |
   | **Background Color** | **Automatic**, **Yellow**, **Green**, **Blue**. |

1. Review the selection. To reset that particular attribute, choose
   **Automatic** in the same submenu.

Automatic font and size are Segoe UI and 11 pt. Automatic colors remove the
explicit color or highlight and use the editor's defaults. These commands
affect selected text immediately and preserve its other formatting. They do
not set a formatting preference for future typing with no selection.
<!-- Verified from: src/gui/menus/format.py [build_format_menu]; src/gui/views/root_window.py [_set_font_family, _set_font_size, _set_text_color, _set_background_color]; src/gui/views/text_buffer.py [apply_selection_font_family, apply_selection_font_size, _apply_selection_color_component]; src/domains/documents/models.py [DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE] -->

### Create, continue, or remove a list

1. Put the cursor on a line, or select several lines.
1. Choose **Format > Bullet List** or **Format > Numbered List**.
1. Type an item, then press **Enter** at its end to continue the list.
1. Press **Enter** on an empty list item to remove that marker and end the list.

Applying a list replaces existing bullet or number markers on the affected
lines. Newly applied numbering begins at `1.`. If every affected line already
uses the chosen kind of list, selecting that command removes its markers.
Selecting through the start of the next line excludes that next line.
<!-- Verified from: src/gui/views/text_buffer.py [_get_affected_lines, toggle_bullet_list, toggle_numbered_list, handle_return_in_list]; src/gui/views/root_window.py [_toggle_bullet_list, _toggle_numbered_list, _handle_return] -->

Lists are ordinary text prefixes. Automatic continuation recognizes `•`, `·`,
`-`, or `*`, or a number followed by `.` or `)`, followed by a space or tab at
the beginning of the line. Continuing a numbered item increases its number by
one. Renumbering later lines after edits is not automatic.
<!-- Verified from: src/gui/views/text_buffer.py [_BULLET_RE, _NUMBER_RE, handle_return_in_list] -->

### Insert and edit a simple table

1. Put the cursor where the table should begin.
1. Choose **Format > Insert Table**.
1. Replace **Column 1**, **Column 2**, and the two **Cell** placeholders.
1. Keep tabs between columns and line breaks between rows. Add or remove text
   as you would elsewhere in the document.

The command inserts a two-column, two-row text template. If the cursor is
mid-line, the table starts on a new line. The cursor moves to the first header.
This is tab-separated text, with no separate cell or table-properties dialog.
<!-- Verified from: src/gui/menus/format.py [build_format_menu]; src/gui/views/text_buffer.py [insert_table] -->

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
<!-- Verified from: src/gui/views/root_window.py [IMAGE_FILE_TYPES, _insert_image]; src/gui/views/images.py [insert_image_at, insert_image_bytes_at_cursor]; src/domains/documents/images.py [decode_image]; src/domains/documents/plain_text_rtf.py [_format_image] -->

### Paste an image or text

1. Copy text, a bitmap image, or image files to the Windows clipboard.
1. Click in the editor to set the insertion cursor.
1. Press **Ctrl+V** to paste.

A clipboard bitmap is inserted as PNG. When the clipboard contains file paths,
the first readable image is inserted. A successful image paste reports
**Pasted image**. If no usable image is available, ordinary text paste is used.
<!-- Verified from: src/gui/views/root_window.py [_build_editor, _handle_paste]; src/gui/views/images.py [look_clipboard_image_bytes] -->

### Drop image files into a note

1. Place the insertion cursor at the desired position in your document.
1. Drag one or more image files from Windows File Explorer onto the text area.
1. Review the inserted images and save the document.

Files are inserted at the current insertion cursor. Unreadable or unsupported
files are skipped. If none can be inserted, the status reads
**Dropped file is not a supported image**. Use **File > Open...** to open a
document; dropping files is an image insertion action.
<!-- Verified from: src/gui/views/root_window.py [_register_drop_target, _handle_drop]; src/gui/views/images.py [insert_image_bytes_at_cursor] -->

### Remove an embedded image

1. Select the image's position in the document along with any text you intend
   to remove.
1. Press **Delete**, then review the surrounding text.
1. Save to persist the removal.

Each image occupies one position in the document. Only images still present
in the text area are included when saving.
<!-- Verified from: src/gui/views/root_window.py [_build_editor, _save_document]; src/gui/views/text_buffer.py [read_document_from_text, _look_image_name_at] -->

### Look up help while working

1. Open **Help**.
1. Choose **Keyboard Shortcuts** for the application shortcuts, **RTF Support**
   for the supported document features, or **About RTF Editor** for a brief
   description.
1. Dismiss the dialog to resume editing.
<!-- Verified from: src/gui/menus/help.py [build_help_menu, show_keyboard_shortcuts, show_rtf_support, show_about] -->

## Settings and Preferences

Not Applicable.

There is no user preferences dialog or user-editable settings file. The
**Format** choices described above change document content, take effect
immediately, and persist in that document when saved. They are not global
preferences for later documents or sessions.
<!-- Verified from: src/gui/menus/menu.py [build_menu_bar]; src/gui/menus/format.py [build_format_menu]; src/gui/views/root_window.py [__init__, _save_document]; src/domains/documents/plain_text_rtf.py [_format_style_attributes] -->

## Importing and Exporting

Use **File > Open...**, **Save**, and **Save As...** for native documents.
There is no separate import/export command or conversion to Microsoft RTF,
DOCX, PDF, or HTML. Plain text files without the required header do not open
as documents; paste their text into a new note instead.
<!-- Verified from: src/gui/menus/file.py [build_file_menu]; src/gui/views/root_window.py [_open_file, _save_document, _save_document_as, _handle_paste]; src/domains/documents/plain_text_rtf.py [parse_plain_text_rtf] -->

| Input or output | How to use it | Rules |
| --- | --- | --- |
| Plain Text RTF | Open with **File > Open...**; write with **Save** or **Save As...**. | UTF-8, `PTRTF/1` header, valid markers; normally `.rtf`. |
| Image files | Insert, paste, or drop them using the tasks above. | Must decode as an image; stored inside the document as PNG or JPEG. |
| Clipboard text | Paste into the document. | Ordinary text paste is used when the clipboard supplies no usable image. |
<!-- Verified from: src/adapters/files.py [read_rtf, write_rtf]; src/gui/views/root_window.py [_insert_image, _handle_paste, _handle_drop]; src/domains/documents/images.py [decode_image] -->

The destination is the path you select in **Save document**, not an automatic
export folder. Repeated image insertions add more images; they do not replace
earlier copies. Saving overwrites the destination file. For the native file
layout and a complete text example, see [Your Data Files](#your-data-files).
<!-- Verified from: src/gui/views/root_window.py [_save_document_as]; src/gui/views/images.py [insert_image_at]; src/adapters/files.py [write_rtf] -->

## Commands and Shortcuts

### Launch from a terminal

| Command or argument | Accepted values | What it does |
| --- | --- | --- |
| `.venv/Scripts/python.exe -m src.main` | Optional document path. | Opens the desktop editor. |
| `plain-rtf` | Optional document path. | Installed equivalent of the module command. |
| First argument | An existing Plain Text RTF file path; quote spaces. | Opens that document at startup. |
| Additional arguments | Ignored. | No additional action. |
<!-- Verified from: pyproject.toml [project.gui-scripts]; src/main.py [_get_startup_path, main] -->

No named command-line options are defined. For example, `--help` would be
treated as a filename; use the **Help** menu for assistance.
<!-- Verified from: src/main.py [_get_startup_path]; src/gui/menus/help.py [build_help_menu] -->

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
<!-- Verified from: src/gui/menus/file.py [build_file_menu]; src/gui/menus/format.py [build_format_menu]; src/gui/menus/help.py [build_help_menu]; src/gui/views/root_window.py [_bind_shortcuts] -->

The editing area also supports these Windows text shortcuts:

| Shortcut | Action |
| --- | --- |
| **Ctrl+C** | Copy selected text. |
| **Ctrl+X** | Cut selected text. |
| **Ctrl+V** | Paste an image when available, otherwise text. |
| **Ctrl+Z** | Undo a text edit. |
| **Ctrl+Y** | Redo a text edit. |
<!-- Verified from: src/gui/views/root_window.py [_build_editor, _handle_paste] -->

In the editing area, **Enter** continues a list or inserts an ordinary line
break. On an empty list item it removes the marker. **Ctrl+V** uses the image
or text paste behavior described above.
<!-- Verified from: src/gui/views/root_window.py [_build_editor, _handle_return, _handle_paste]; src/gui/views/text_buffer.py [handle_return_in_list] -->

## Your Data Files

### Locate documents and diagnostic logs

| File | Location | Purpose and editing guidance |
| --- | --- | --- |
| Your `.rtf` documents | The folder you choose when saving. | Stores text, formatting, and embedded images. May be edited as UTF-8 text using the rules below. |
| Original image files | Wherever you selected them. | Read when inserted; the document stores its own image content. |
| `logs/rtf-editor.log` | Under the project folder when running from source; under `plain-rtf-data/` beside a portable executable; under `%LOCALAPPDATA%/plain-rtf/` for an installed application. | Diagnostic output. Read it when investigating problems; it is not a document or preferences file. |
| `logs/rtf-editor.1.log` through `logs/rtf-editor.3.log` | Beside the main log. | Older diagnostic output retained as the log rotates at approximately 1,000,000 bytes. |
<!-- Verified from: src/adapters/files.py [read_rtf, write_rtf]; src/gui/views/root_window.py [_save_document_as]; src/domains/documents/plain_text_rtf.py [_format_image]; src/gui/app.py [launch_app]; src/config/path_handler.py [LOGS_DIR, APP_ROOT]; src/config/logging/log_config.py [configure_logging, _rotating_handler_factory] -->

The portable executable needs a writable folder. Its application data stays
beside it and is not redirected to AppData if that folder cannot be written.
If **Cannot write application data** appears, move the executable to a writable
folder and try again. Your documents still use the paths you select when saving.
The portable data folder follows the executable's name: `My Notes.exe` uses
`My Notes-data/`. Rename its existing data folder too if you want to retain
the logs when renaming the executable.
<!-- Verified from: src/config/path_handler.py [STORAGE_MODE, ROOT_DIR]; src/gui/app.py [_show_storage_error]; src/gui/views/root_window.py [_save_document_as] -->

Use **Save As...** to change a document's storage location. Save or close the
document before editing its file elsewhere, then reopen it to load those
changes. An already-open document does not refresh from external edits, and
its next save writes its current contents over the file.
<!-- Verified from: src/gui/views/root_window.py [_open_path, _save_document, _save_document_as]; src/adapters/files.py [write_rtf] -->

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
<!-- Verified from: src/adapters/files.py [read_rtf, write_rtf]; src/domains/documents/plain_text_rtf.py [parse_plain_text_rtf, _read_attributes, _read_style, _BodyReader] -->

A style starts with `[[name=value]]` and ends with `[[/]]`. Combine attributes
inside the opening marker using semicolons. Do not nest style spans. Line
breaks and tabs in the body remain line breaks and tabs in the document.
<!-- Verified from: src/domains/documents/plain_text_rtf.py [_read_attributes, _BodyReader, parse_plain_text_rtf] -->

| Attribute | Accepted value | Default when omitted or invalid |
| --- | --- | --- |
| `font` | A percent-encoded family name, such as `Segoe%20UI`. | Segoe UI. |
| `size` | Positive integer points, such as `14`. | 11 pt. |
| `color` | Lowercase hex color, such as `#ff0000`. | Automatic text color. |
| `background` | Lowercase hex color, such as `#fff59d`. | No explicit highlight. |
| `bold`, `italic`, `underline`, `strikethrough` | `true` enables the attribute; `false` disables it. | Disabled; only exact `true` enables it. |
<!-- Verified from: src/domains/documents/plain_text_rtf.py [_read_style, _look_positive_integer, _look_color, _look_font_family, _look_enabled]; src/domains/documents/models.py [DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE] -->

Attribute names must contain lowercase letters and cannot repeat within a
marker. Unknown attributes are ignored. Unavailable fonts retain their saved
names; their on-screen appearance depends on font availability on the computer.
<!-- Verified from: src/domains/documents/plain_text_rtf.py [_read_attributes, _read_style, _format_style_attributes]; src/gui/views/text_buffer.py [_ensure_style_tag, _look_style] -->

Escape literal markup characters in text as follows:

| Character wanted | Write in the file |
| --- | --- |
| `[` | `\[` |
| `]` | `\]` |
| `\` | `\\` |
<!-- Verified from: src/domains/documents/plain_text_rtf.py [_escape_text, _read_escape] -->

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
<!-- Verified from: src/domains/documents/plain_text_rtf.py [_format_image, _read_image] -->

## Troubleshooting

| Symptom | Likely Cause | Resolution |
| --- | --- | --- |
| **Open failed** says **This file is not a Plain Text RTF document.** | The first line is not exactly `PTRTF/1`, or the file uses another format. | Open a native document. For ordinary text, paste into a new note; renaming a Microsoft RTF file does not convert it. |
| **Open failed** reports an unclosed marker, unclosed style span, or nested style spans. | Hand-edited markup is incomplete or nested. | Correct the file using the native-format rules above and reopen it. |
| **Open failed** reports invalid image data or a format mismatch. | An embedded image marker or payload is invalid. | Correct the image marker or remove it in a text editor, then reinsert the original image through **Insert Image...**. |
| **Open failed** reports a file access or decoding error. | The path cannot be read, or the file is not UTF-8. | Choose a readable native document and ensure hand-edited files are saved as UTF-8. The current document remains open. |
<!-- Verified from: src/gui/views/root_window.py [_open_path]; src/adapters/files.py [read_rtf]; src/domains/documents/plain_text_rtf.py [parse_plain_text_rtf, _BodyReader, _read_image] -->

| Symptom | Likely Cause | Resolution |
| --- | --- | --- |
| **Save failed** | The selected destination cannot be written. | Read the error, then use **Save As...** to select an existing writable folder. Unsaved changes remain in the editor. |
| **Select text to format it**, **Select text to change its font**, **Select text to resize it**, or **Select text to color it** | No text is selected. | Select the text and repeat the command. |
| **Insert image failed** | The selected file is unreadable or cannot be decoded as an image. | Choose a readable supported image file. |
| **Dropped file is not a supported image** | None of the dropped files could be inserted as images. | Drop readable images; use **File > Open...** for documents. |
| Pasting copied files inserts only one image. | Clipboard file paste selects the first readable image. | Drop multiple files onto the editor to insert several images. |
| A list keeps adding markers when you press **Enter**. | The current line is a recognized list item. | Press **Enter** on an empty list item, or toggle the matching list command to remove markers. |
| A wide image appears smaller. | Image display is reduced to fit the text area. | This is expected; PNG and JPEG source bytes are preserved in the document. |
<!-- Verified from: src/gui/views/root_window.py [_save_document, _set_font_family, _set_font_size, _set_text_color, _set_background_color, _toggle_style, _insert_image, _handle_drop]; src/gui/views/images.py [look_clipboard_image_bytes, insert_image_at]; src/gui/views/text_buffer.py [handle_return_in_list]; src/domains/documents/images.py [decode_image] -->

For file errors, use the dialog's message first. The diagnostic log location
is listed above, but open/save errors are shown in dialogs and are not
explicitly written to that log.
<!-- Verified from: src/gui/views/root_window.py [_open_path, _save_document]; src/config/logging/log_config.py [configure_logging] -->

## FAQ

### Can I open Microsoft Word RTF files?

No. The native format requires the `PTRTF/1` header and has its own formatting
markers. The `.rtf` extension alone does not establish compatibility.
<!-- Verified from: src/gui/menus/help.py [RTF_SUPPORT_TEXT]; src/domains/documents/plain_text_rtf.py [parse_plain_text_rtf] -->

### Does the editor save automatically?

No. Use **Save** or **Save As...**. New, Open, and Exit prompt when there are
unsaved changes; **Cancel** lets you return to the current document.
<!-- Verified from: src/gui/views/root_window.py [_save_document, _new_file, _open_file, _on_close, _prompt_for_unsaved_changes] -->

### Do I need to send image files with my document?

No. Inserted images are embedded in the saved document as PNG or JPEG data.
<!-- Verified from: src/domains/documents/plain_text_rtf.py [_format_image, _read_image] -->

### Can I choose a custom font size or color?

The menus offer the sizes and colors listed above. Hand-edited native files
can specify other positive integer point sizes and lowercase `#rrggbb`
colors. There is no custom size entry field or color picker in the menus.
<!-- Verified from: src/gui/menus/format.py [build_format_menu]; src/domains/documents/plain_text_rtf.py [_look_positive_integer, _look_color] -->

### Why does changing bold affect the whole selection?

The command enables bold across the selection unless every selected character
is already bold, in which case it removes bold. Italic, underline, and
strikethrough follow the same rule.
<!-- Verified from: src/gui/views/text_buffer.py [toggle_selection_style] -->

### Are tables and lists special document objects?

No. Tables use tabs and line breaks; lists use visible text prefixes. You can
edit their text directly, and list commands help add or remove the prefixes.
<!-- Verified from: src/gui/views/text_buffer.py [insert_table, toggle_bullet_list, toggle_numbered_list] -->

## Glossary

| Term | Meaning |
| --- | --- |
| Plain Text RTF | This editor's UTF-8 document format, identified by `PTRTF/1`. |
| Selection | Text highlighted for replacement, removal, or formatting. |
| Insertion cursor | The position where typing or an inserted image appears. |
| Inline formatting | Font, size, colors, bold, italic, underline, or strikethrough applied to text. |
| Embedded image | Image content stored inside the document file. |
| Marker | A `[[...]]` instruction in the native file that describes styling or an image. |
| Unsaved changes | Edits not yet written to the document's file, indicated by a leading `*` in the title. |
<!-- Verified from: src/domains/documents/plain_text_rtf.py [FORMAT_HEADER, _format_styled_text, _format_image]; src/gui/views/text_buffer.py [_look_selection_range]; src/gui/views/images.py [insert_image_bytes_at_cursor]; src/gui/views/root_window.py [_update_title] -->
