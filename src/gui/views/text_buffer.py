"""Map editor widget state to and from document models.

- Represents each character's style as Tk tags: one font tag per distinct
  font style plus optional `fg_<hex>` and `bg_<hex>` color tags.
- Keeps per-widget tag and font registries keyed weakly by widget;
  `create_style_tags` must run before a widget is loaded or styled.
- Embedded images count as one character, matching the document model's
  object replacement placeholder.
"""

from __future__ import annotations

import re
from contextlib import suppress
from dataclasses import replace
from tkinter import TclError, Text
from tkinter import font as tkfont
from typing import Literal
from weakref import WeakKeyDictionary

from src.domains.documents.content import iter_text_images
from src.domains.documents.images import replace_image_offset
from src.domains.documents.models import (
    DEFAULT_FONT_FAMILY,
    DEFAULT_FONT_SIZE,
    OBJECT_REPLACEMENT_CHAR,
    DocumentModel,
    ImageRef,
    TextSpan,
    TextStyle,
)
from src.gui.views.images import (
    clear_images,
    init_image_registry,
    insert_image_at,
    look_image_ref,
)

StyleName = Literal["bold", "italic", "underline", "strikethrough"]
DEFAULT_STYLE = TextStyle()
BASE_FONT_REGISTRY: WeakKeyDictionary[Text, tkfont.Font] = WeakKeyDictionary()
FONT_REGISTRY: WeakKeyDictionary[Text, list[tkfont.Font]] = WeakKeyDictionary()
STYLE_TAGS_BY_WIDGET: WeakKeyDictionary[Text, dict[TextStyle, str]] = (
    WeakKeyDictionary()
)
STYLE_BY_TAG_BY_WIDGET: WeakKeyDictionary[Text, dict[str, TextStyle]] = (
    WeakKeyDictionary()
)
FOREGROUND_TAG_PREFIX = "fg_"
BACKGROUND_TAG_PREFIX = "bg_"
_HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def _normalize_style_key(style: TextStyle) -> TextStyle:
    """Return the style with its colors cleared for font tag lookup.

    Colors live on separate tags, so styles that differ only in color
    share one font tag.
    """
    return replace(
        style,
        foreground_color=None,
        background_color=None,
    )


def _ensure_style_tag(text_widget: Text, style: TextStyle) -> str:
    """Return the font tag for a style, creating it on first use.

    - Ignores the style's colors; see `_normalize_style_key`.
    - A new tag gets a copy of the widget's base font configured for the
      style, with unset family and size falling back to the defaults.
    - Registers the new font and tag in the per-widget registries.
    """
    style_key = _normalize_style_key(style)
    style_tags = STYLE_TAGS_BY_WIDGET[text_widget]
    if style_key in style_tags:
        return style_tags[style_key]

    base_font = BASE_FONT_REGISTRY[text_widget]
    style_font = base_font.copy()
    style_font.configure(
        family=style_key.font_family or DEFAULT_FONT_FAMILY,
        size=style_key.font_size or DEFAULT_FONT_SIZE,
        weight="bold" if style_key.bold else "normal",
        slant="italic" if style_key.italic else "roman",
        underline=style_key.underline,
        overstrike=style_key.strikethrough,
    )
    tag_name = f"style_{len(style_tags)}"
    text_widget.tag_configure(tag_name, font=style_font)
    FONT_REGISTRY[text_widget].append(style_font)
    style_tags[style_key] = tag_name
    STYLE_BY_TAG_BY_WIDGET[text_widget][tag_name] = style_key
    return tag_name


def _look_style(text_widget: Text, index: str) -> TextStyle:
    """Return the full style of the character at an index.

    - Combines the font tag's style with any foreground and background
      color tags present at the index.
    - Returns the default style, without colors, when no tags apply.
    """
    style = DEFAULT_STYLE
    foreground_color = None
    background_color = None

    for tag_name in reversed(text_widget.tag_names(index)):
        if tag_name in STYLE_BY_TAG_BY_WIDGET[text_widget]:
            style = STYLE_BY_TAG_BY_WIDGET[text_widget][tag_name]
        if tag_name.startswith(FOREGROUND_TAG_PREFIX):
            foreground_color = tag_name.removeprefix(FOREGROUND_TAG_PREFIX)
        if tag_name.startswith(BACKGROUND_TAG_PREFIX):
            background_color = tag_name.removeprefix(BACKGROUND_TAG_PREFIX)

    return replace(
        style,
        foreground_color=foreground_color,
        background_color=background_color,
    )


def _ensure_color_tag(
    text_widget: Text,
    color_value: str,
    *,
    tag_prefix: str,
    option_name: str,
) -> str:
    """Return the color tag for a color, creating it on first use.

    - The tag name is the prefix followed by the color value.
    - Returns an empty string, creating no tag, when the tag does not exist
      yet and the value is not a `#rrggbb` hex color.
    """
    color_tag_name = f"{tag_prefix}{color_value}"
    if color_tag_name not in text_widget.tag_names():
        if not _HEX_COLOR_RE.match(color_value):
            return ""
        text_widget.tag_configure(color_tag_name, **{option_name: color_value})
    return color_tag_name


def _look_tags_for_style(
    text_widget: Text,
    style: TextStyle,
) -> tuple[str, ...]:
    """Return the tags that render a style, creating any that are missing.

    - The font tag always comes first.
    - Color tags follow only for set colors; invalid colors are dropped.
    """
    tag_names = [_ensure_style_tag(text_widget, style)]
    if style.foreground_color is not None:
        foreground_tag = _ensure_color_tag(
            text_widget,
            style.foreground_color,
            tag_prefix=FOREGROUND_TAG_PREFIX,
            option_name="foreground",
        )
        if foreground_tag:
            tag_names.append(foreground_tag)
    if style.background_color is not None:
        background_tag = _ensure_color_tag(
            text_widget,
            style.background_color,
            tag_prefix=BACKGROUND_TAG_PREFIX,
            option_name="background",
        )
        if background_tag:
            tag_names.append(background_tag)
    return tuple(tag_names)


def _apply_style(text_widget: Text, index: str, style: TextStyle) -> None:
    """Replace the style of the single character at an index.

    Removes every font and color tag from that character, then adds the
    tags for the new style.
    """
    next_index = text_widget.index(f"{index} +1c")
    for tag_name in STYLE_BY_TAG_BY_WIDGET[text_widget]:
        text_widget.tag_remove(tag_name, index, next_index)
    for tag_name in text_widget.tag_names(index):
        if tag_name.startswith((FOREGROUND_TAG_PREFIX, BACKGROUND_TAG_PREFIX)):
            text_widget.tag_remove(tag_name, index, next_index)

    for tag_name in _look_tags_for_style(text_widget, style):
        text_widget.tag_add(tag_name, index, next_index)


def _replace_style_flag(
    current_style: TextStyle,
    style_name: StyleName,
    *,
    should_enable: bool,
) -> TextStyle:
    """Return a copy of the style with one formatting flag set.

    Any style name other than bold, italic, or underline updates the
    strikethrough flag.
    """
    if style_name == "bold":
        return replace(current_style, bold=should_enable)
    if style_name == "italic":
        return replace(current_style, italic=should_enable)
    if style_name == "underline":
        return replace(current_style, underline=should_enable)
    return replace(current_style, strikethrough=should_enable)


def _replace_style_color(
    current_style: TextStyle,
    field_name: Literal["foreground_color", "background_color"],
    color_value: str | None,
) -> TextStyle:
    """Return a copy of the style with one color field replaced.

    A color of None resets the field to the automatic color.
    """
    if field_name == "foreground_color":
        return replace(current_style, foreground_color=color_value)
    return replace(current_style, background_color=color_value)


def _look_selection_range(text_widget: Text) -> tuple[str, str] | None:
    """Return the start and end indexes of the selection.

    Returns None when nothing is selected.
    """
    try:
        return text_widget.index("sel.first"), text_widget.index("sel.last")
    except TclError:
        return None


def _count_indices(text_widget: Text, start: str, end: str) -> int:
    """Count index positions between two indexes.

    - Characters and embedded images each count as one position.
    - Returns 0 when Tk reports no count.
    """
    result = text_widget.count(start, end, "indices")
    if result is None:
        return 0
    if isinstance(result, (tuple, list)):
        return int(result[0])
    return int(result)


def count_document_characters(text_widget: Text) -> int:
    """Return the document length counting images as one character.

    Tk's trailing newline is not counted.
    """
    return _count_indices(text_widget, "1.0", "end-1c")


def create_style_tags(text_widget: Text) -> None:
    """Prepare a text widget to host styled editor content.

    - Sets the widget font to a copy of TkTextFont using the default family
      and size.
    - Resets the widget's font, tag, and image registries, then creates the
      tag for the default style.
    - Must run before any other function in this module uses the widget.
    """
    base_font = tkfont.nametofont("TkTextFont").copy()
    base_font.configure(family=DEFAULT_FONT_FAMILY, size=DEFAULT_FONT_SIZE)
    text_widget.configure(font=base_font)

    BASE_FONT_REGISTRY[text_widget] = base_font
    FONT_REGISTRY[text_widget] = [base_font]
    STYLE_TAGS_BY_WIDGET[text_widget] = {}
    STYLE_BY_TAG_BY_WIDGET[text_widget] = {}
    init_image_registry(text_widget)
    _ensure_style_tag(text_widget, DEFAULT_STYLE)


def load_document_into_text(text_widget: Text, document: DocumentModel) -> None:
    """Render a document model into the editor widget.

    - Replaces all existing text and registered images.
    - Each object replacement character becomes the image whose offset
      matches its position; a placeholder with no matching image, or with
      unreadable image data, is dropped.
    - Clears the widget's modified flag, but does not reset undo history.
    """
    text_widget.delete("1.0", "end")
    clear_images(text_widget)
    images_by_offset = {image.offset: image for image in document.images}
    offset = 0
    for span in document.spans:
        tags = _look_tags_for_style(text_widget, span.style)
        for text, image_ref in iter_text_images(
            span.text, offset, images_by_offset
        ):
            text_widget.insert("end", text, tags)
            if image_ref is not None:
                # Corrupt image data must not block document open; drop
                # the image like the writer drops unmatched placeholders.
                with suppress(OSError):
                    insert_image_at(text_widget, "end-1c", image_ref)
        offset += len(span.text)

    is_modified = False
    text_widget.edit_modified(is_modified)


def _look_image_name_at(text_widget: Text, index: str) -> str | None:
    """Return the Tk image name embedded at an index, if any."""
    for key, value, _position in text_widget.dump(index, image=True):
        if key == "image":
            return value
    return None


def read_document_from_text(text_widget: Text) -> DocumentModel:
    """Collect a document model from the editor widget.

    - Groups consecutive characters with equal styles into one span.
    - Each registered embedded image becomes an object replacement
      character plus an image entry anchored at that character's offset.
    - Embedded images that are not registered are skipped.
    - Tk's trailing newline is excluded; an empty widget yields a document
      with no spans.
    """
    end_index = text_widget.index("end-1c")
    if _count_indices(text_widget, "1.0", end_index) == 0:
        return DocumentModel(spans=())

    spans: list[TextSpan] = []
    images: list[ImageRef] = []
    text_buffer: list[str] = []
    index = "1.0"
    offset = 0
    active_style = _look_style(text_widget, index)

    while text_widget.compare(index, "<", end_index):
        next_index = text_widget.index(f"{index} +1c")
        current_style = _look_style(text_widget, index)
        if current_style != active_style and text_buffer:
            spans.append(
                TextSpan(text="".join(text_buffer), style=active_style),
            )
            text_buffer.clear()
            active_style = current_style

        current_char = text_widget.get(index, next_index)
        if current_char:
            text_buffer.append(current_char)
            offset += 1
        else:
            image_name = _look_image_name_at(text_widget, index)
            image_ref = (
                look_image_ref(text_widget, image_name)
                if image_name is not None
                else None
            )
            if image_ref is not None:
                text_buffer.append(OBJECT_REPLACEMENT_CHAR)
                images.append(replace_image_offset(image_ref, offset))
                offset += 1
        index = next_index

    if text_buffer:
        spans.append(TextSpan(text="".join(text_buffer), style=active_style))

    return DocumentModel(
        spans=tuple(spans),
        images=tuple(images),
    )


def toggle_selection_style(text_widget: Text, style_name: StyleName) -> bool:
    """Toggle a formatting attribute across the selected text.

    - Turns the attribute off when every selected character already has
      it, and on for the whole selection otherwise.
    - Other style attributes, including colors, are preserved.
    - Returns False without changes when nothing is selected.
    """
    selection_range = _look_selection_range(text_widget)
    if selection_range is None:
        return False

    start_index, end_index = selection_range
    current_styles: list[TextStyle] = []
    scan_index = start_index
    while text_widget.compare(scan_index, "<", end_index):
        current_styles.append(_look_style(text_widget, scan_index))
        scan_index = text_widget.index(f"{scan_index} +1c")

    if not current_styles:
        return False

    should_enable = not all(
        getattr(style, style_name) for style in current_styles
    )
    update_index = start_index
    while text_widget.compare(update_index, "<", end_index):
        current_style = _look_style(text_widget, update_index)
        next_style = _replace_style_flag(
            current_style,
            style_name,
            should_enable=should_enable,
        )
        _apply_style(text_widget, update_index, next_style)
        update_index = text_widget.index(f"{update_index} +1c")

    return True


def _apply_selection_color_component(
    text_widget: Text,
    *,
    field_name: Literal["foreground_color", "background_color"],
    color_value: str | None,
) -> bool:
    """Apply one color field across the selected text.

    - A color of None resets the field to the automatic color.
    - A value that is not a `#rrggbb` hex color is not rendered and
      leaves the field reading back as automatic.
    - Returns False without changes when nothing is selected.
    """
    selection_range = _look_selection_range(text_widget)
    if selection_range is None:
        return False

    start_index, end_index = selection_range
    update_index = start_index
    while text_widget.compare(update_index, "<", end_index):
        current_style = _look_style(text_widget, update_index)
        next_style = _replace_style_color(
            current_style,
            field_name,
            color_value,
        )
        _apply_style(text_widget, update_index, next_style)
        update_index = text_widget.index(f"{update_index} +1c")

    return True


def apply_selection_color(
    text_widget: Text,
    foreground_color: str | None,
) -> bool:
    """Apply a text color across the selected text.

    - A color of None resets the text to the automatic color.
    - Returns False without changes when nothing is selected.
    """
    return _apply_selection_color_component(
        text_widget,
        field_name="foreground_color",
        color_value=foreground_color,
    )


def apply_selection_background_color(
    text_widget: Text,
    background_color: str | None,
) -> bool:
    """Apply a background color across the selected text.

    - A color of None resets the background to the automatic color.
    - Returns False without changes when nothing is selected.
    """
    return _apply_selection_color_component(
        text_widget,
        field_name="background_color",
        color_value=background_color,
    )


def apply_selection_font_size(
    text_widget: Text,
    font_size: int | None,
) -> bool:
    """Apply a font size across the selected text.

    - A size of None resets the text to the default font size.
    - Other style attributes, including colors, are preserved.
    - Returns False without changes when nothing is selected.
    """
    selection_range = _look_selection_range(text_widget)
    if selection_range is None:
        return False

    start_index, end_index = selection_range
    update_index = start_index
    while text_widget.compare(update_index, "<", end_index):
        current_style = _look_style(text_widget, update_index)
        next_style = replace(current_style, font_size=font_size)
        _apply_style(text_widget, update_index, next_style)
        update_index = text_widget.index(f"{update_index} +1c")

    return True


def apply_selection_font_family(
    text_widget: Text,
    font_family: str | None,
) -> bool:
    """Apply a font family across the selected text.

    - A family of None resets the text to the default font family.
    - Other style attributes, including colors, are preserved.
    - Returns False without changes when nothing is selected.
    """
    selection_range = _look_selection_range(text_widget)
    if selection_range is None:
        return False

    start_index, end_index = selection_range
    update_index = start_index
    while text_widget.compare(update_index, "<", end_index):
        current_style = _look_style(text_widget, update_index)
        next_style = replace(current_style, font_family=font_family)
        _apply_style(text_widget, update_index, next_style)
        update_index = text_widget.index(f"{update_index} +1c")

    return True


_BULLET_PREFIX = "\u2022 "
_BULLET_RE = re.compile(r"^[\u2022\u00b7\-*][\t ]")
_NUMBER_RE = re.compile(r"^(\d+)([.)])[\t ]")
_LIST_RE = re.compile(r"^(?:[\u2022\u00b7\-*][\t ]|\d+[.)][\t ])")


def _get_affected_lines(text_widget: Text) -> tuple[int, int]:
    """Return the first and last line numbers a list command applies to.

    - Uses the selected lines, or the cursor line when nothing is selected.
    - A multi-line selection ending at column 0 excludes that final line.
    """
    selection = _look_selection_range(text_widget)
    if selection is not None:
        first = int(selection[0].split(".")[0])
        last = int(selection[1].split(".")[0])
        if int(selection[1].split(".")[1]) == 0 and last > first:
            last -= 1
        return first, last
    line = int(text_widget.index("insert").split(".")[0])
    return line, line


def toggle_bullet_list(text_widget: Text) -> bool:
    """Toggle bullet list markers on the current or selected lines.

    - Removes the markers when every affected line is already bulleted.
    - Otherwise replaces any existing bullet or number marker on each line
      with a bullet.
    - Always returns True.
    """
    first, last = _get_affected_lines(text_widget)

    all_bulleted = all(
        _BULLET_RE.match(text_widget.get(f"{n}.0", f"{n}.end") or "")
        for n in range(first, last + 1)
    )

    for n in range(first, last + 1):
        line = text_widget.get(f"{n}.0", f"{n}.end")
        match = _LIST_RE.match(line or "")
        if match:
            text_widget.delete(f"{n}.0", f"{n}.{match.end()}")
        if not all_bulleted:
            text_widget.insert(f"{n}.0", _BULLET_PREFIX)

    return True


def toggle_numbered_list(text_widget: Text) -> bool:
    """Toggle numbered list markers on the current or selected lines.

    - Removes the markers when every affected line is already numbered.
    - Otherwise replaces any existing bullet or number marker on each line
      with a number counting up from 1.
    - Always returns True.
    """
    first, last = _get_affected_lines(text_widget)

    all_numbered = all(
        _NUMBER_RE.match(text_widget.get(f"{n}.0", f"{n}.end") or "")
        for n in range(first, last + 1)
    )

    for n in range(first, last + 1):
        line = text_widget.get(f"{n}.0", f"{n}.end")
        match = _LIST_RE.match(line or "")
        if match:
            text_widget.delete(f"{n}.0", f"{n}.{match.end()}")
        if not all_numbered:
            text_widget.insert(f"{n}.0", f"{n - first + 1}. ")

    return True


def handle_return_in_list(text_widget: Text) -> str | None:
    """Continue a bulleted or numbered list when Enter is pressed.

    - Returns "break" when Enter was handled, so the default Text binding
      is suppressed, or None to fall through to the default newline.
    - Falls through when text is selected, the line is not a list item, or
      the cursor is inside the marker.
    - An empty list item exits the list by stripping its marker.
    - A numbered item continues with the next number and the same
      separator; a bullet item continues with a bullet.
    """
    try:
        if text_widget.index("sel.first") != text_widget.index("sel.last"):
            return None
    except TclError:
        pass

    cursor = text_widget.index("insert")
    line_str, col_str = cursor.split(".")
    line_num = int(line_str)
    col = int(col_str)
    line = text_widget.get(f"{line_num}.0", f"{line_num}.end")

    bullet_match = _BULLET_RE.match(line)
    number_match = _NUMBER_RE.match(line)
    match = bullet_match or number_match
    if match is None:
        return None

    prefix_end = match.end()
    if col < prefix_end:
        return None

    if not line[prefix_end:]:
        text_widget.delete(f"{line_num}.0", f"{line_num}.{prefix_end}")
        return "break"

    if number_match is not None:
        number = int(number_match.group(1)) + 1
        separator = number_match.group(2)
        new_prefix = f"{number}{separator} "
    else:
        new_prefix = _BULLET_PREFIX

    text_widget.insert("insert", f"\n{new_prefix}")
    return "break"


def insert_table(text_widget: Text) -> bool:
    """Insert a 2-column table template at the cursor.

    - The template is a tab-separated header row and one body row.
    - Starts a new line first when the cursor is not at a line start.
    - Moves the cursor to the start of the header row.
    - Always returns True.
    """
    cursor = text_widget.index("insert")
    col = int(cursor.split(".")[1])
    prefix = "\n" if col > 0 else ""
    text_widget.insert("insert", f"{prefix}Column 1\tColumn 2\nCell\tCell\n")
    target_line = int(cursor.split(".")[0]) + (1 if col > 0 else 0)
    text_widget.mark_set("insert", f"{target_line}.0")
    return True
