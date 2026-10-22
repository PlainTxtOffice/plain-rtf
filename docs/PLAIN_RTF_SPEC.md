---
last_updated: 2026-10-21
version: 1.0.0
format_version: "PTRTF/1"
product_version: "0.1.0"
---

# Plain Text RTF Specification

This document describes the Plain Text RTF format implemented by Plain RTF
0.1.0. It defines the current file syntax, reader behavior, and serialization
rules for implementers and people editing documents as text. The document
revision above is independent of the format identifier `PTRTF/1`.

Plain Text RTF is a custom format, not Microsoft Rich Text Format. The app
normally uses the `.rtf` extension, but changing a file's extension does not
convert its contents. Microsoft RTF control words and groups are not supported.
See the [user manual](USER_MANUAL.md) for editor operations.

## Encoding and Header

Files use UTF-8 without a byte-order mark (BOM). The first line must be exactly
`PTRTF/1`, with no leading or trailing whitespace. A BOM is not stripped by
the reader and therefore causes header validation to fail. Other format
versions are rejected.

The writer emits `PTRTF/1` followed by LF (`U+000A`), then the document body.
The reader also accepts a header alone as an empty document. Before parsing,
it normalizes CRLF and bare CR to LF throughout the input. Writers should use
LF for document line breaks.

All content after the header's line ending belongs to the body. Spaces, tabs,
blank lines, and a final body newline are text content; the reader does not
trim them. The writer does not add a final newline after a nonempty body.

## Body and Markers

The body contains Unicode text, escape sequences, style spans, and inline
image markers. Marker syntax is case-sensitive.

| Construct | Syntax | Meaning |
| --- | --- | --- |
| Style start | `[[name=value;name=value]]` | Start a text style. |
| Style end | `[[/]]` | End the current style span. |
| Image | `[[image=png;width=40;height=20;payload=...]]` | Insert one inline image. |

An opening marker ends at the first following `]]`. Its content is a nonempty
list of assignments separated by semicolons. Each assignment splits at its
first `=`; subsequent equals signs remain part of the value, including Base64
padding. Attribute names must match `[a-z]+` and must be unique within the
marker. Empty assignments, trailing semicolons, duplicate names, and names
containing uppercase letters, spaces, digits, or punctuation are rejected.
Whitespace is not trimmed from names or values. There is no quoted-value syntax.

A marker containing the attribute `image` is always parsed as an image marker.
Every other attribute marker starts a style span, even when all its attributes
are unknown. There is no comment, metadata, or extension-block syntax.

## Text Escapes

Outside marker attributes, these two-character sequences represent literals:

| File text | Decoded character |
| --- | --- |
| ` \\ ` | Backslash (`U+005C`) |
| `\[` | Left square bracket (`U+005B`) |
| `\]` | Right square bracket (`U+005D`) |

The writer escapes every backslash and square bracket in text. The reader
preserves a backslash before any other character, including a trailing
backslash. For example, `\n` is a literal backslash followed by `n`, not a line
break. Use an actual LF for a line break.

An unescaped `[[` starts a marker. A lone `[` and unescaped closing brackets
are ordinary text unless they form part of a recognized marker. Escape rules
do not apply inside attribute values; use the value encoding specified below.

## Text Styles

A style span has the form `[[attributes]]text[[/]]`. It may cross line breaks
and may contain images, but it must not contain another style span. Combine
attributes in one marker to apply several styles to the same text. A stray
end marker, nested style span, or missing end marker is an error.

Each span starts from the default style. Fields omitted from its marker use
their defaults. After `[[/]]`, ordinary text returns to the default style.

| Attribute | Interoperable value | Default / invalid-value behavior |
| --- | --- | --- |
| `font` | Nonempty UTF-8 percent-encoded font family, such as `Times%20New%20Roman` | Empty or absent means editor default. |
| `size` | Positive decimal integer | Invalid or absent means editor default. |
| `color` | Lowercase `#rrggbb`, such as `#ff0000` | Invalid or absent means editor default. |
| `bold` | `true` | Any other value or absence means off. |
| `italic` | `true` | Any other value or absence means off. |
| `underline` | `true` | Any other value or absence means off. |
| `strikethrough` | `true` | Any other value or absence means off. |
| `background` | Lowercase `#rrggbb`, such as `#fff59d` | Invalid or absent means editor default. |

Unknown style attributes are ignored. Invalid style values fall back per field;
they do not invalidate the whole marker. For example, `color=#FF0000` is ignored
because uppercase hexadecimal digits are not accepted. The format does not
embed fonts or guarantee identical rendering on different computers. The
current editor's default font is Segoe UI, size 11; defaults are not stored in
an unformatted span.

Font names use percent encoding, not form encoding: a space is `%20`, and `+`
does not mean space. The writer uses UTF-8 percent encoding, leaving ASCII
letters, digits, `-`, `.`, `_`, and `~` unescaped. The current reader uses
Python's permissive `urllib.parse.unquote` behavior; malformed percent escapes
are not separately rejected. Writers should always emit valid encodings.

For numeric attributes, the reader accepts positive values recognized by
Python's `str.isdecimal()` and `int()`, including leading zeros and Unicode
decimal digits. Signs, decimal points, and surrounding whitespace are invalid.
Writers should emit ordinary ASCII decimal digits without leading zeros. No
format-level upper bound is specified; runtime limits can still reject values
or make them impractical to render.

## Embedded Images

An image marker is self-contained and has no end marker. It requires all four
attributes below, in any order:

| Attribute | Requirement |
| --- | --- |
| `image` | Exactly `png` or `jpeg`. |
| `width` | Positive integer display width in pixels. |
| `height` | Positive integer display height in pixels. |
| `payload` | Standard Base64 encoding of the complete PNG or JPEG bytes. |

The reader uses strict Base64 decoding: whitespace, line wrapping, and invalid
Base64 characters are rejected. The decoded payload must load successfully
with Pillow, and its detected format must match `image`. Actual pixel width
and height come from the encoded image. The marker's dimensions describe the
display size and may differ from those actual dimensions.

Unknown additional image attributes are ignored. Style attributes on an image
marker do not style surrounding text. An image inside a style span is accepted;
the reader assigns that span's style to the internal image placeholder.

PNG and JPEG are the only formats stored in image markers. The editor can
convert other readable image formats to PNG when inserting them; that import
conversion does not extend the file format. Image markers contain embedded
bytes, not filesystem paths or remote URLs.

## Lists, Tables, and Document Model

Lists and tables have no dedicated marker syntax. List prefixes are ordinary
text. Tables use tabs and line breaks. Their appearance and editing commands
are editor behavior, not separate document structures.

Internally, a document contains styled text spans and image references. Each
image occupies one `U+FFFC` OBJECT REPLACEMENT CHARACTER in the concatenated
text. Image offsets count Python Unicode string positions, not UTF-8 bytes or
user-perceived grapheme clusters; each image consumes one position. Offsets
and original image dimensions are derived during parsing, not stored as marker
attributes.

Reserve `U+FFFC` for images. A literal occurrence without an image reference
can be read as text but is dropped on serialization. Image references without
a matching placeholder are not emitted. Programmatic document producers must
keep placeholders and image offsets consistent; the writer does not validate
the entire model before emitting it.

## Serialization and Round Trips

The writer emits the header and merges adjacent spans with equal styles,
dropping empty input spans. Default-style text has no style wrapper. Nondefault
text uses attributes in this order: `font`, `size`, `color`, `bold`, `italic`,
`underline`, `strikethrough`, `background`. Unset fields and false flags are
omitted. Image attributes are written as `image`, `width`, `height`, `payload`.

Images are emitted outside style wrappers. Styled text before and after an
image is wrapped separately; this can produce empty style wrappers at image
boundaries. An input image's placeholder style is consequently not guaranteed
to survive a parse/write cycle. Stored image bytes and display dimensions are
preserved by the codec for consistent models.

Round trips preserve supported content rather than the original file spelling.
Attribute order, redundant spans, unknown attributes, invalid style values,
escape spelling, font encoding, numeric spelling, and line endings can change.
Do not use byte equality as the definition of equivalent documents. Unknown
attributes are discarded, so this reader is not a lossless editor for future
format extensions.

## Examples

A complete document with plain text and combined formatting:

```text
PTRTF/1
A plain line.
[[font=Times%20New%20Roman;size=18;color=#ff0000;bold=true;italic=true]]Styled text[[/]]
Literal markers: \[\[bold=true\]\] and a backslash: \\
```

An empty document is `PTRTF/1` followed by LF. The following image form is
schematic: replace `BASE64_PNG_BYTES` with an actual Base64 PNG payload before
parsing it.

```text
PTRTF/1
Before [[image=png;width=40;height=20;payload=BASE64_PNG_BYTES]] after.
```

## Errors and Implementation References

Malformed headers, marker syntax, style boundaries, and invalid image content
are rejected rather than silently treated as ordinary text. The codec normally
reports these as `PlainTextRtfError`, a `ValueError` subclass. UTF-8 decoding,
filesystem, resource-limit, and image-library failures can occur separately.
The format defines no document-size, image-count, or decoded-pixel budget;
readers handling untrusted files should set their own resource limits.

This specification is grounded in these implementation and test sources:

- [Codec](../src/domains/documents/plain_text_rtf.py): header, marker parsing,
  attribute handling, image validation, and serialization.
- [Document models](../src/domains/documents/models.py) and
  [content traversal](../src/domains/documents/content.py): styles, offsets,
  placeholder handling, and span normalization.
- [File adapter](../src/adapters/files.py): UTF-8 reading and LF writing.
- [Image import](../src/domains/documents/images.py): image conversion before
  storage.
- [Codec tests](../tests/domains/documents/test_plain_text_rtf.py) and
  [file tests](../tests/adapters/test_files.py): round trips and rejection
  cases.

Changes to the codec should update this specification and relevant tests in
the same change. A future incompatible syntax needs an explicit versioning
decision; the current reader accepts only `PTRTF/1`.
