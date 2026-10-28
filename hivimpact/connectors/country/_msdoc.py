"""
Text of a Word 97 to 2003 binary document (.doc), read with the Python standard library alone.

Why the project writes a Word reader. The Tajik Ministry of Health publishes the HIV chapter of
the 2017 yearbook as a Word 97 file, and the project installs no package for Word files. A
converter which prints the text with no cell boundary (macOS textutil, for example) glues the
entries of a table row together, and "200" and "219" print as "200219", which loses the figure
of every table entry. The reader below keeps the cell mark of the Word format (character 7,
which module _msdoc returns unchanged), and a table row then reads as a separate entry for every
figure.

What the reader does. A .doc file is a Compound File Binary (CFB) container. The reader follows
the file allocation table of the container to the "WordDocument" stream and to the table stream
("0Table" or "1Table", named by bit nine of the flags word of the File Information Block), reads the
piece table (the Clx structure, located by the fcClx and lcbClx fields of the File Information
Block), and joins the pieces, decoding a compressed piece as cp1252 and an uncompressed piece as
UTF-16LE. The layouts follow the Microsoft specifications [MS-CFB] and [MS-DOC]. Fields, pictures
and embedded charts come back as the control characters of the Word format, and a caller reads
only the table text.

Failure. A file which is not a compound file, a sector chain which loops or runs past the end of
the allocation table, a document which is not Word 97 or later, and a table stream with no piece
table all raise ValueError, and the caller emits no row.
"""
from __future__ import annotations

import struct
from typing import Dict, List

_CFB_MAGIC = bytes.fromhex("D0CF11E0A1B11AE1")
_LAST_REGULAR_SECTOR = 0xFFFFFFFA   # sector numbers from here up are markers, not sectors
_WORD_IDENT = 0xA5EC


def _chain(start: int, table: List[int]) -> List[int]:
    out: List[int] = []
    seen = set()
    while start < _LAST_REGULAR_SECTOR:
        if start in seen or start >= len(table):
            raise ValueError("the compound file holds a broken sector chain")
        seen.add(start)
        out.append(start)
        start = table[start]
    return out


def cfb_streams(blob: bytes) -> Dict[str, bytes]:
    """{stream name: stream bytes} for every stream of a Compound File Binary container."""
    if blob[:8] != _CFB_MAGIC:
        raise ValueError("the file is not a compound file")
    shift, mini_shift = struct.unpack_from("<HH", blob, 0x1E)
    size, mini_size = 1 << shift, 1 << mini_shift
    (dir_start,) = struct.unpack_from("<I", blob, 0x30)
    cutoff, mini_fat_start, n_mini_fat, difat_start, n_difat = struct.unpack_from("<5I", blob, 0x38)

    def sector(n: int) -> bytes:
        return blob[(n + 1) * size:(n + 2) * size]

    difat = list(struct.unpack_from("<109I", blob, 0x4C))
    nxt = difat_start
    for _ in range(n_difat):
        vals = struct.unpack(f"<{size // 4}I", sector(nxt))
        difat.extend(vals[:-1])
        nxt = vals[-1]
    fat: List[int] = []
    for s in difat:
        if s < _LAST_REGULAR_SECTOR:
            fat.extend(struct.unpack(f"<{size // 4}I", sector(s)))
    directory = b"".join(sector(s) for s in _chain(dir_start, fat))
    entries = []
    for i in range(0, len(directory) - 127, 128):
        e = directory[i:i + 128]
        name_len = struct.unpack_from("<H", e, 64)[0]
        name = e[:max(name_len - 2, 0)].decode("utf-16-le", "replace")
        start, length = struct.unpack_from("<IQ", e, 116)
        entries.append((name, e[66], start, length & 0xFFFFFFFF))
    if not entries:
        raise ValueError("the compound file holds no directory entry")
    root_start = entries[0][2]
    mini_stream = (b"".join(sector(s) for s in _chain(root_start, fat))
                   if root_start < _LAST_REGULAR_SECTOR else b"")
    mini_fat: List[int] = []
    if n_mini_fat:
        for s in _chain(mini_fat_start, fat):
            mini_fat.extend(struct.unpack(f"<{size // 4}I", sector(s)))
    streams: Dict[str, bytes] = {}
    for name, kind, start, length in entries:
        if kind != 2:   # 2 marks a stream, 1 a storage and 5 the root
            continue
        if length < cutoff:
            data = b"".join(mini_stream[s * mini_size:(s + 1) * mini_size]
                            for s in _chain(start, mini_fat))
        else:
            data = b"".join(sector(s) for s in _chain(start, fat))
        streams[name] = data[:length]
    return streams


def doc_text(blob: bytes) -> str:
    """The text of a Word 97 to 2003 document, with the Word control characters kept (character 7
    ends a table cell and a table row, character 13 ends a paragraph, character 12 breaks a
    page)."""
    streams = cfb_streams(blob)
    if "WordDocument" not in streams:
        raise ValueError("the compound file holds no WordDocument stream")
    wd = streams["WordDocument"]
    if struct.unpack_from("<H", wd, 0)[0] != _WORD_IDENT:
        raise ValueError("the WordDocument stream is not Word 97 or later")
    flags = struct.unpack_from("<H", wd, 0x0A)[0]
    table_name = "1Table" if flags & 0x0200 else "0Table"
    if table_name not in streams:
        raise ValueError(f"the compound file holds no {table_name} stream")
    table = streams[table_name]
    # File Information Block: a 32-byte base, then counted arrays of 16-bit and 32-bit values,
    # then the offset and length pairs, of which pair 33 locates the piece table (Clx)
    pos = 32
    pos += 2 + 2 * struct.unpack_from("<H", wd, pos)[0]
    pos += 2 + 4 * struct.unpack_from("<H", wd, pos)[0]
    pos += 2
    fc_clx, lcb_clx = struct.unpack_from("<II", wd, pos + 33 * 8)
    clx = table[fc_clx:fc_clx + lcb_clx]
    i = 0
    while i < len(clx) and clx[i] == 0x01:   # property modifiers ahead of the piece table
        i += 3 + struct.unpack_from("<h", clx, i + 1)[0]
    if i >= len(clx) or clx[i] != 0x02:
        raise ValueError("the table stream holds no piece table")
    lcb = struct.unpack_from("<I", clx, i + 1)[0]
    plc = clx[i + 5:i + 5 + lcb]
    n = (lcb - 4) // 12
    cps = struct.unpack_from(f"<{n + 1}I", plc, 0)
    parts = []
    for k in range(n):
        fc = struct.unpack_from("<I", plc, 4 * (n + 1) + 8 * k + 2)[0]
        length = cps[k + 1] - cps[k]
        if fc & 0x40000000:
            offset = (fc & 0x3FFFFFFF) // 2
            parts.append(wd[offset:offset + length].decode("cp1252", "replace"))
        else:
            parts.append(wd[fc:fc + 2 * length].decode("utf-16-le", "replace"))
    return "".join(parts)
