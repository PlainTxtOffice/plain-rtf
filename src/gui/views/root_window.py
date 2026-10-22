"""Define the main desktop window for the lightweight editor.

- Wires menus, keyboard shortcuts, paste, and file drops to the text
  buffer and image helpers.
- Delegates document file I/O to the injected document adapter.
- Reports failures through message boxes and the status bar.
"""

from __future__ import annotations

import logging
import tkinter as tk
from functools import partial
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkfont
from typing import TYPE_CHECKING, Protocol, cast

from tkinterdnd2 import DND_FILES, TkinterDnD  # type: ignore[import-untyped]

from src.config.path_handler import ASSETS_DIR
from src.domains.documents.models import DocumentModel
from src.gui.menus.file import FileMenuActions
from src.gui.menus.format import FormatMenuActions
from src.gui.menus.help import (
    HelpMenuActions,
    show_about,
    show_keyboard_shortcuts,
    show_rtf_support,
)
from src.gui.menus.menu import (
    MenuBarActions,
    build_menu_bar,
)
from src.gui.views.images import (
    insert_image_bytes_at_cursor,
    look_clipboard_image_bytes,
)
from src.gui.views.text_buffer import (
    StyleName,
    apply_selection_background_color,
    apply_selection_color,
    apply_selection_font_family,
    apply_selection_font_size,
    count_document_characters,
    create_style_tags,
    handle_return_in_list,
    insert_table,
    load_document_into_text,
    read_document_from_text,
    toggle_bullet_list,
    toggle_numbered_list,
    toggle_selection_style,
)

if TYPE_CHECKING:
    from src.adapters.document import DocumentAdapter


class _DropEvent(Protocol):
    """Minimal drag-and-drop event surface used by the root window."""

    data: str


class _DropTargetText(Protocol):
    """Text widget surface extended by tkinterdnd2 for drop registration."""

    def drop_target_register(self, *dnd_types: str) -> object:
        """Register one or more drag-and-drop target types."""

    def dnd_bind(self, sequence: str, callback: object) -> object:
        """Bind a drag-and-drop event callback."""


logger = logging.getLogger(__name__)


class RootWindow(TkinterDnD.Tk):
    """Host the editor menu bar, text area, status bar, and file actions.

    - Tracks the current file path and a dirty flag that drives the title
      and status bar; a None path means an unsaved new document.
    - Prompts to save unsaved changes before replacing the document or
      closing the window.
    - Construction builds the whole UI and loads an empty document; call
      `run` to start the event loop.
    """

    def __init__(
        self,
        document_adapter: DocumentAdapter,
        startup_path: Path | None = None,
    ) -> None:
        """Build the window and load the starting document.

        - Starts with an empty untitled document.
        - When a startup path is given, opens it; an open failure shows an
          error dialog and leaves the empty document in place.
        """
        super().__init__()
        self._document_adapter = document_adapter
        self._current_path: Path | None = None
        self._is_dirty = False
        self._ignore_modified = False
        self._icon_image: tk.PhotoImage | None = None
        self._font_families = tuple(sorted(set(tkfont.families(self))))
        self._status_text = tk.StringVar(value="Ready")
        self._char_count_text = tk.StringVar(value="0 characters")

        self.title("RTF Editor")
        self.geometry("920x640")
        self.minsize(640, 480)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._configure_window_icon()

        self._build_menu_bar()
        self._build_editor()
        self._register_drop_target()
        self._build_status_bar()
        self._bind_shortcuts()
        self._load_document(DocumentModel(spans=()))
        if startup_path is not None:
            self._open_path(startup_path)

    def run(self) -> None:
        """Run the Tk event loop until the window is destroyed."""
        self.mainloop()

    def _configure_window_icon(self) -> None:
        """Set the window icon from the bundled PNG and ICO assets.

        - Each icon file is optional; a missing file is skipped.
        - A file Tk cannot load is logged at debug level and skipped.
        - Keeps a reference to the PNG image so Tk does not discard it.
        """
        icon_png_path = ASSETS_DIR / "rtf_editor_icon.png"
        icon_ico_path = ASSETS_DIR / "rtf_editor_icon.ico"

        if icon_png_path.exists():
            try:
                self._icon_image = tk.PhotoImage(file=str(icon_png_path))
                set_as_default_icon = True
                self.iconphoto(set_as_default_icon, self._icon_image)
            except tk.TclError:
                logger.debug("Failed to load PNG icon from %s", icon_png_path)
                self._icon_image = None

        if not icon_ico_path.exists():
            return

        try:
            self.iconbitmap(str(icon_ico_path))
        except tk.TclError:
            logger.debug("Failed to load ICO icon from %s", icon_ico_path)

    def _build_menu_bar(self) -> None:
        """Build the menu bar and connect its items to window actions."""
        build_menu_bar(
            self,
            MenuBarActions(
                file_menu=FileMenuActions(
                    new_file=self._new_file,
                    open_file=self._open_file,
                    save_file=self._save_file,
                    save_file_as=self._save_file_as,
                    close_window=self._on_close,
                ),
                format_menu=FormatMenuActions(
                    toggle_bold=self._toggle_bold,
                    toggle_italic=self._toggle_italic,
                    toggle_underline=self._toggle_underline,
                    toggle_strikethrough=self._toggle_strikethrough,
                    set_font_family=self._set_font_family,
                    set_font_size_auto=self._set_font_size_auto,
                    set_font_size_10=self._set_font_size_10,
                    set_font_size_11=self._set_font_size_11,
                    set_font_size_12=self._set_font_size_12,
                    set_font_size_14=self._set_font_size_14,
                    set_font_size_18=self._set_font_size_18,
                    set_color_auto=self._set_text_color_auto,
                    set_color_black=self._set_text_color_black,
                    set_color_red=self._set_text_color_red,
                    set_color_green=self._set_text_color_green,
                    set_color_blue=self._set_text_color_blue,
                    set_background_auto=self._set_background_color_auto,
                    set_background_yellow=self._set_background_color_yellow,
                    set_background_green=self._set_background_color_green,
                    set_background_blue=self._set_background_color_blue,
                    toggle_bullet_list=self._toggle_bullet_list,
                    toggle_numbered_list=self._toggle_numbered_list,
                    insert_table=self._insert_table,
                    insert_image=self._insert_image,
                ),
                help_menu=HelpMenuActions(
                    show_keyboard_shortcuts=partial(
                        show_keyboard_shortcuts,
                        self,
                    ),
                    show_rtf_support=partial(show_rtf_support, self),
                    show_about=partial(show_about, self),
                ),
                font_families=self._font_families,
            ),
        )

    def _build_editor(self) -> None:
        """Create the scrollable text widget and its event bindings.

        - Enables undo on the widget.
        - Binds modification, Return, and paste events to window handlers.
        - Prepares the widget's style tags for document rendering.
        """
        editor_frame = ttk.Frame(self, padding=8)
        editor_frame.grid(row=1, column=0, sticky="nsew")
        editor_frame.columnconfigure(0, weight=1)
        editor_frame.rowconfigure(0, weight=1)

        self.text = tk.Text(
            editor_frame,
            wrap="word",
            undo=True,
            autoseparators=True,
            padx=12,
            pady=12,
        )
        self.text.grid(row=0, column=0, sticky="nsew")
        self.text.bind("<<Modified>>", self._handle_modified)
        self.text.bind("<Return>", self._handle_return)
        self.text.bind("<<Paste>>", self._handle_paste)

        scroll_bar = ttk.Scrollbar(
            editor_frame,
            orient="vertical",
            command=self.text.yview,
        )
        scroll_bar.grid(row=0, column=1, sticky="ns")
        self.text.configure(yscrollcommand=scroll_bar.set)

        create_style_tags(self.text)

    def _build_status_bar(self) -> None:
        """Create the status message and character count labels."""
        status_frame = ttk.Frame(self)
        status_frame.grid(row=2, column=0, sticky="ew")
        status_frame.columnconfigure(0, weight=1)

        status_label = ttk.Label(
            status_frame,
            textvariable=self._status_text,
            anchor="w",
            padding=(10, 0, 10, 8),
        )
        status_label.grid(row=0, column=0, sticky="w")

        char_count_label = ttk.Label(
            status_frame,
            textvariable=self._char_count_text,
            anchor="e",
            padding=(10, 0, 10, 8),
        )
        char_count_label.grid(row=0, column=1, sticky="e")

    def _bind_shortcuts(self) -> None:
        """Bind file and formatting keyboard shortcuts.

        Each shortcut is bound on both the window and the text widget so
        the handler's "break" result suppresses the Text class defaults.
        """
        shortcut_handlers = (
            ("<Control-n>", self._new_file),
            ("<Control-o>", self._open_file),
            ("<Control-s>", self._save_file),
            ("<Control-S>", self._save_file_as),
            ("<Control-b>", self._toggle_bold),
            ("<Control-i>", self._toggle_italic),
            ("<Control-u>", self._toggle_underline),
        )
        for sequence, handler in shortcut_handlers:
            self.bind(sequence, handler)
            # Bind on the Text widget too: its handlers run before the
            # Text class bindings, so returning "break" suppresses the
            # built-in Control-o newline and Control-i tab insertions.
            self.text.bind(sequence, handler)

    def _handle_return(self, _event: tk.Event[tk.Misc]) -> str | None:
        """Continue list items on Return; otherwise allow the default."""
        return handle_return_in_list(self.text)

    def _handle_modified(self, _event: tk.Event[tk.Misc]) -> None:
        """Mark the document dirty after a user edit.

        - Always clears the widget's modified flag so the next edit fires
          the event again.
        - Ignores events raised while a document is being loaded.
        - Refreshes the character count after each user edit.
        """
        if self._ignore_modified or not self.text.edit_modified():
            is_modified = False
            self.text.edit_modified(is_modified)
            return

        is_modified = False
        self.text.edit_modified(is_modified)
        self._mark_dirty()
        self._update_char_count()

    def _update_char_count(self) -> None:
        """Show the document length in the status bar.

        Embedded images count as one character each.
        """
        count = count_document_characters(self.text)
        label = "1 character" if count == 1 else f"{count:,} characters"
        self._char_count_text.set(label)

    def _mark_dirty(self) -> None:
        """Flag unsaved changes in the title and status bar.

        Does nothing when the document is already dirty.
        """
        if self._is_dirty:
            return

        self._is_dirty = True
        self._update_title()
        self._status_text.set("Unsaved changes")

    def _set_saved_state(self) -> None:
        """Clear the dirty flag and report the saved state.

        The status reads "New document" when no file path is set, and
        names the saved file otherwise.
        """
        self._is_dirty = False
        self._update_title()
        if self._current_path is None:
            self._status_text.set("New document")
            return
        self._status_text.set(f"Saved {self._current_path.name}")

    def _update_title(self) -> None:
        """Show the file name, or Untitled, with a * prefix when dirty."""
        prefix = "*" if self._is_dirty else ""
        file_label = (
            self._current_path.name if self._current_path else "Untitled"
        )
        self.title(f"{prefix}{file_label} - RTF Editor")

    def _prompt_for_unsaved_changes(self) -> bool:
        """Ask whether to save unsaved changes before continuing.

        - Returns True without prompting when the document is clean.
        - Returns False when the user cancels.
        - Returns True when the user declines to save.
        - When the user chooses to save, returns whether the save succeeded.
        """
        if not self._is_dirty:
            return True

        save_choice = messagebox.askyesnocancel(
            title="Unsaved changes",
            message="Save your changes before continuing?",
            parent=self,
        )
        if save_choice is None:
            return False
        if not save_choice:
            return True
        return self._save_document()

    def _load_document(
        self,
        document: DocumentModel,
    ) -> None:
        """Replace the editor content with a document.

        - Resets undo history and marks the document as saved.
        - Does not change the current file path; callers set it first.
        - Moves keyboard focus to the editor.
        """
        self._ignore_modified = True
        load_document_into_text(self.text, document)
        self.text.edit_reset()
        self._ignore_modified = False
        self._set_saved_state()
        self._update_char_count()
        self.text.focus_set()

    def _read_document(self) -> DocumentModel:
        return read_document_from_text(self.text)

    def _new_file(self, _event: tk.Event[tk.Misc] | None = None) -> str:
        """Replace the editor content with an empty untitled document.

        - Does nothing when the user cancels the unsaved-changes prompt.
        - Returns "break" to stop further Tk event handling.
        """
        if not self._prompt_for_unsaved_changes():
            return "break"

        self._current_path = None
        self._load_document(DocumentModel(spans=()))
        self._status_text.set("New document")
        return "break"

    def _open_path(self, file_path: Path) -> bool:
        """Load a document file into the editor.

        - Does not prompt about unsaved changes; callers handle that.
        - On a read or decode failure, shows an error dialog, keeps the
          current document, and returns False.
        - On success, makes the file the current path and returns True.
        """
        try:
            result = self._document_adapter.load_document(file_path)
        except (OSError, ValueError, UnicodeDecodeError) as error:
            messagebox.showerror(
                title="Open failed",
                message=str(error),
                parent=self,
            )
            return False

        self._current_path = file_path
        self._load_document(result)
        self._status_text.set(f"Opened {file_path.name}")
        return True

    def _open_file(self, _event: tk.Event[tk.Misc] | None = None) -> str:
        """Ask for a document file and open it.

        - Does nothing when the user cancels the unsaved-changes prompt or
          the file dialog.
        - Returns "break" to stop further Tk event handling.
        """
        if not self._prompt_for_unsaved_changes():
            return "break"

        selected_path = filedialog.askopenfilename(
            parent=self,
            title="Open document",
            filetypes=(("RTF documents", "*.rtf"), ("All files", "*.*")),
        )
        if not selected_path:
            return "break"

        file_path = Path(selected_path)
        self._open_path(file_path)
        return "break"

    def _save_file(self, _event: tk.Event[tk.Misc] | None = None) -> str:
        """Save the document from a menu item or shortcut.

        Returns "break" to stop further Tk event handling.
        """
        self._save_document()
        return "break"

    def _save_file_as(self, _event: tk.Event[tk.Misc] | None = None) -> str:
        """Save the document under a new path from a menu or shortcut.

        Returns "break" to stop further Tk event handling.
        """
        self._save_document_as()
        return "break"

    def _save_document(self) -> bool:
        """Write the editor content to the current path.

        - Asks for a path first when the document is untitled.
        - On a write failure, shows an error dialog, leaves the dirty flag
          unchanged, and returns False.
        - On success, marks the document saved and returns True.
        """
        if self._current_path is None:
            return self._save_document_as()

        try:
            self._document_adapter.save_document(
                self._current_path,
                self._read_document(),
            )
        except OSError as error:
            messagebox.showerror(
                title="Save failed",
                message=str(error),
                parent=self,
            )
            return False

        self._set_saved_state()
        return True

    def _save_document_as(self) -> bool:
        """Ask for a path and save the document there.

        - Returns False when the user cancels the dialog.
        - The chosen path becomes the current path only when the save
          succeeds; on failure the previous path is restored.
        """
        selected_path = filedialog.asksaveasfilename(
            parent=self,
            title="Save document",
            defaultextension=".rtf",
            filetypes=(("RTF documents", "*.rtf"),),
        )
        if not selected_path:
            return False

        previous_path = self._current_path
        self._current_path = Path(selected_path)
        saved = self._save_document()
        if not saved:
            self._current_path = previous_path
        return saved

    def _toggle_style(self, style_name: StyleName) -> str:
        """Toggle a formatting attribute on the selection.

        - With no selection, only shows a status hint.
        - Otherwise marks the document dirty and refocuses the editor.
        - Returns "break" to stop further Tk event handling.
        """
        if not toggle_selection_style(self.text, style_name):
            self._status_text.set("Select text to format it")
            return "break"

        self._mark_dirty()
        self._status_text.set(f"Updated {style_name} formatting")
        self.text.focus_set()
        return "break"

    def _set_text_color(
        self,
        foreground_color: str | None,
        color_label: str,
    ) -> str:
        """Apply a text color to the selection.

        - A color of None resets the selection to the automatic color.
        - With no selection, only shows a status hint.
        - Otherwise marks the document dirty and refocuses the editor.
        - Returns "break" to stop further Tk event handling.
        """
        if not apply_selection_color(self.text, foreground_color):
            self._status_text.set("Select text to color it")
            return "break"

        self._mark_dirty()
        self._status_text.set(f"Updated text color to {color_label}")
        self.text.focus_set()
        return "break"

    def _set_font_size(
        self,
        font_size: int | None,
        size_label: str,
    ) -> str:
        """Apply a font size to the selection.

        - A size of None resets the selection to the default size.
        - With no selection, only shows a status hint.
        - Otherwise marks the document dirty and refocuses the editor.
        - Returns "break" to stop further Tk event handling.
        """
        if not apply_selection_font_size(self.text, font_size):
            self._status_text.set("Select text to resize it")
            return "break"

        self._mark_dirty()
        self._status_text.set(f"Updated font size to {size_label}")
        self.text.focus_set()
        return "break"

    def _set_font_family(
        self,
        font_family: str | None,
    ) -> str:
        """Apply a font family to the selection.

        - A family of None resets the selection to the default family.
        - With no selection, only shows a status hint.
        - Otherwise marks the document dirty and refocuses the editor.
        - Returns "break" to stop further Tk event handling.
        """
        if not apply_selection_font_family(self.text, font_family):
            self._status_text.set("Select text to change its font")
            return "break"

        self._mark_dirty()
        font_label = font_family or "automatic"
        self._status_text.set(f"Updated font to {font_label}")
        self.text.focus_set()
        return "break"

    def _set_background_color(
        self,
        background_color: str | None,
        color_label: str,
    ) -> str:
        """Apply a background color to the selection.

        - A color of None resets the selection to the automatic background.
        - With no selection, only shows a status hint.
        - Otherwise marks the document dirty and refocuses the editor.
        - Returns "break" to stop further Tk event handling.
        """
        if not apply_selection_background_color(self.text, background_color):
            self._status_text.set("Select text to color it")
            return "break"

        self._mark_dirty()
        self._status_text.set(f"Updated background color to {color_label}")
        self.text.focus_set()
        return "break"

    def _set_text_color_auto(self) -> str:
        return self._set_text_color(None, "automatic")

    def _set_text_color_black(self) -> str:
        return self._set_text_color("#000000", "black")

    def _set_text_color_red(self) -> str:
        return self._set_text_color("#ff0000", "red")

    def _set_text_color_green(self) -> str:
        return self._set_text_color("#008000", "green")

    def _set_text_color_blue(self) -> str:
        return self._set_text_color("#0000ff", "blue")

    def _set_font_size_auto(self) -> str:
        return self._set_font_size(None, "automatic")

    def _set_font_size_10(self) -> str:
        return self._set_font_size(10, "10 pt")

    def _set_font_size_11(self) -> str:
        return self._set_font_size(11, "11 pt")

    def _set_font_size_12(self) -> str:
        return self._set_font_size(12, "12 pt")

    def _set_font_size_14(self) -> str:
        return self._set_font_size(14, "14 pt")

    def _set_font_size_18(self) -> str:
        return self._set_font_size(18, "18 pt")

    def _set_background_color_auto(self) -> str:
        return self._set_background_color(None, "automatic")

    def _set_background_color_yellow(self) -> str:
        return self._set_background_color("#fff59d", "yellow")

    def _set_background_color_green(self) -> str:
        return self._set_background_color("#c8e6c9", "green")

    def _set_background_color_blue(self) -> str:
        return self._set_background_color("#bbdefb", "blue")

    def _toggle_bullet_list(self) -> str:
        """Toggle bullet markers on the current or selected lines.

        Marks the document dirty, refocuses the editor, and returns "break".
        """
        toggle_bullet_list(self.text)
        self._mark_dirty()
        self._status_text.set("Toggled bullet list")
        self.text.focus_set()
        return "break"

    def _toggle_numbered_list(self) -> str:
        """Toggle number markers on the current or selected lines.

        Marks the document dirty, refocuses the editor, and returns "break".
        """
        toggle_numbered_list(self.text)
        self._mark_dirty()
        self._status_text.set("Toggled numbered list")
        self.text.focus_set()
        return "break"

    def _insert_table(self) -> str:
        """Insert a 2-column table template at the cursor.

        Marks the document dirty, refocuses the editor, and returns "break".
        """
        insert_table(self.text)
        self._mark_dirty()
        self._status_text.set("Inserted table")
        self.text.focus_set()
        return "break"

    IMAGE_FILE_TYPES = (
        ("Images", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
        ("All files", "*.*"),
    )

    def _insert_image(self) -> str:
        """Ask for an image file and insert it at the cursor.

        - Does nothing when the user cancels the file dialog.
        - Shows an error dialog when the file cannot be read or is not a
          supported image.
        - On success, marks the document dirty and updates the status bar.
        - Returns "break" to stop further Tk event handling.
        """
        selected_path = filedialog.askopenfilename(
            parent=self,
            title="Insert image",
            filetypes=self.IMAGE_FILE_TYPES,
        )
        if not selected_path:
            return "break"

        file_path = Path(selected_path)
        try:
            image_bytes = self._document_adapter.read_image_bytes(file_path)
        except OSError as error:
            messagebox.showerror(
                title="Insert image failed",
                message=str(error),
                parent=self,
            )
            return "break"

        if not insert_image_bytes_at_cursor(self.text, image_bytes):
            messagebox.showerror(
                title="Insert image failed",
                message=(f"{file_path.name} is not a supported image file."),
                parent=self,
            )
            return "break"

        self._mark_dirty()
        self._update_char_count()
        self._status_text.set(f"Inserted {file_path.name}")
        self.text.focus_set()
        return "break"

    def _handle_paste(self, _event: tk.Event[tk.Misc]) -> str | None:
        """Paste a clipboard image at the cursor when one is available.

        - Returns "break" after inserting an image, suppressing the default
          text paste.
        - Returns None to fall back to the default paste when the clipboard
          cannot be read or holds no supported image.
        """
        try:
            # Imported lazily: ImageGrab can fail to import on some
            # platforms, and paste must degrade to plain text there.
            from PIL import ImageGrab  # noqa: PLC0415

            clipboard_content = ImageGrab.grabclipboard()
        except (ImportError, OSError):
            return None

        image_bytes = look_clipboard_image_bytes(clipboard_content)
        if image_bytes is None:
            return None

        if not insert_image_bytes_at_cursor(self.text, image_bytes):
            return None

        self._mark_dirty()
        self._update_char_count()
        self._status_text.set("Pasted image")
        self.text.focus_set()
        return "break"

    def _register_drop_target(self) -> None:
        """Accept dropped files on the text widget."""
        drop_target_text = cast("_DropTargetText", self.text)
        drop_target_text.drop_target_register(DND_FILES)
        drop_target_text.dnd_bind("<<Drop>>", self._handle_drop)

    def _handle_drop(self, event: _DropEvent) -> str:
        """Insert each dropped image file at the cursor.

        - Unreadable files and files that are not supported images are
          skipped silently.
        - Marks the document dirty when at least one image was inserted;
          otherwise only shows a status message.
        - Returns "break" to stop further Tk event handling.
        """
        inserted_any = False
        for raw_path in self.tk.splitlist(event.data):
            file_path = Path(raw_path)
            try:
                image_bytes = self._document_adapter.read_image_bytes(file_path)
            except OSError:
                continue

            if insert_image_bytes_at_cursor(self.text, image_bytes):
                inserted_any = True
                self._status_text.set(f"Inserted {file_path.name}")

        if inserted_any:
            self._mark_dirty()
            self._update_char_count()
            self.text.focus_set()
        else:
            self._status_text.set("Dropped file is not a supported image")
        return "break"

    def _toggle_bold(self, _event: tk.Event[tk.Misc] | None = None) -> str:
        return self._toggle_style("bold")

    def _toggle_italic(self, _event: tk.Event[tk.Misc] | None = None) -> str:
        return self._toggle_style("italic")

    def _toggle_underline(self, _event: tk.Event[tk.Misc] | None = None) -> str:
        return self._toggle_style("underline")

    def _toggle_strikethrough(
        self,
        _event: tk.Event[tk.Misc] | None = None,
    ) -> str:
        return self._toggle_style("strikethrough")

    def _on_close(self) -> None:
        """Destroy the window unless the unsaved-changes prompt cancels."""
        if self._prompt_for_unsaved_changes():
            self.destroy()
