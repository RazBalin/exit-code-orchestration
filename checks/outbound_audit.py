#!/usr/bin/env python3
"""outbound_audit.py: the audit over a text that leaves the workspace.

Reads a .md, .txt, .html or .docx file (every XML part of a .docx, headers and footers included) and
reports, by category:

  CODEPOINT    invisible and bidirectional control characters, the byte-order mark, C0 controls other
               than tab and newline. Blocks.
  CHARACTER    a character the house style forbids (config/workspace.json, outbound.blocked_characters),
               matched by code point, HTML entities included. Blocks.
  PROCESS      a word of the workspace's own machinery (outbound.process_words): an outward text never
               shows the scaffolding that produced it. Blocks.
  PLACEHOLDER  a visible slot or marker: a double-bracketed or double-braced name, or a bracketed note
               to self. Blocks.
  PARAGRAPH    a paragraph over outbound.max_paragraph_words words. Advisory.

Exit 0: no blocking hit. Exit 1: a blocking hit. Exit 2: the file could not be read or read as empty
(an audit that read nothing never reads as clean). --selftest runs synthetic cases.
"""
from __future__ import annotations

import argparse
import html
import pathlib
import re
import shutil
import sys
import tempfile
import zipfile
from collections.abc import Callable

from workspace import config

INVISIBLE = re.compile("[\u200b-\u200f\u202a-\u202e\u2060-\u2064\u2066-\u2069\ufeff\x00-\x08\x0b\x0c\x0e-\x1f]")
NOTE_WORDS = ("TO" + "DO", "T" + "BD", "FIX" + "ME", "VER" + "IFY")
PLACEHOLDER = re.compile(r"\[\[[^\]]*\]\]|\{\{[^}]*\}\}|\[(?:%s)[^\]]*\]|\b(?:%s)\b"
                         % ("|".join(NOTE_WORDS), "|".join(NOTE_WORDS[:3])))
BLOCKING = ("CODEPOINT", "CHARACTER", "PROCESS", "PLACEHOLDER")


def read_text(path: pathlib.Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".docx":
        parts = []
        with zipfile.ZipFile(path) as z:
            for name in sorted(z.namelist()):
                if name.startswith("word/") and name.endswith(".xml"):
                    xml = z.read(name).decode("utf-8", "replace").replace("</w:p>", "\n")
                    parts.append(re.sub(r"<[^>]+>", "", xml))
        return "\n".join(parts)
    text = path.read_text(encoding="utf-8", errors="replace")
    if suffix in (".html", ".htm"):
        text = re.sub(r"(?is)<(script|style)\b.*?</\1>", "", text)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    return text


def audit(text: str, cfg: dict) -> dict:
    out = cfg["outbound"]
    blocked = [re.escape(c) for c in out["blocked_characters"]]
    char_rx = re.compile("|".join(blocked)) if blocked else None
    words = sorted(out["process_words"], key=len, reverse=True)
    proc_rx = re.compile(r"\b(?:%s)s?\b" % "|".join(re.escape(w) for w in words), re.I) if words else None
    hits = {k: [] for k in BLOCKING + ("PARAGRAPH",)}
    lines = text.split("\n")
    for n, line in enumerate(lines, 1):
        for m in INVISIBLE.finditer(line):
            hits["CODEPOINT"].append("line %d: U+%04X" % (n, ord(m.group(0))))
        if char_rx:
            for m in char_rx.finditer(line):
                hits["CHARACTER"].append("line %d: U+%04X" % (n, ord(m.group(0))))
        if proc_rx:
            for m in proc_rx.finditer(line):
                hits["PROCESS"].append("line %d: %s" % (n, m.group(0)))
        for m in PLACEHOLDER.finditer(line):
            hits["PLACEHOLDER"].append("line %d: %s" % (n, m.group(0)))
    para, start = [], 1
    for n, line in enumerate(lines + [""], 1):
        if line.strip():
            start = n if not para else start
            para.append(line)
        elif para:
            words_in = len(" ".join(para).split())
            if words_in > out["max_paragraph_words"] and not para[0].lstrip().startswith(("|", "#", "```")):
                hits["PARAGRAPH"].append("line %d: %d words" % (start, words_in))
            para = []
    return hits


def run(path: pathlib.Path, cfg: dict, quiet: bool = False) -> int:
    try:
        text = read_text(path)
    except (OSError, zipfile.BadZipFile) as e:
        print("[outbound_audit] %s: UNREADABLE (%s)" % (path, e))
        return 2
    if not text.strip():
        print("[outbound_audit] %s: read 0 characters; NOT CLEAN" % path)
        return 2
    hits = audit(text, cfg)
    blocking = [c for c in BLOCKING if hits[c]]
    if not quiet:
        for cat, rows in hits.items():
            if rows:
                kind = "BLOCK" if cat in BLOCKING else "advisory"
                print("  %-11s %-8s %d: %s" % (cat, kind, len(rows), "; ".join(rows[:6])))
    print("[outbound_audit] %s (%d characters read): %s"
          % (path.name, len(text.strip()), "FAIL (%s)" % ", ".join(blocking) if blocking else "PASS"))
    return 1 if blocking else 0


def selftest_cases() -> list[tuple[str, Callable[[], str | None]]]:
    """The synthetic cases, each a (name, function) pair; the function returns None on a pass, else what failed.

    --selftest runs them all; tests/test_selftests.py exposes each one as a unittest test.
    """
    cases = {
        "clean.md": ("The survey recounted plots on six boulders this season.\n", 0),
        "char.md": ("A result " + chr(0xA7) + " strong.\n", 1),
        "entity.html": ("<p>A result &" + "sect; strong.</p>", 1),
        "process.md": ("As the decision list records.\n", 1),
        "slot.md": ("Dear [[name]],\n", 1),
        "note.md": ("Funding: " + NOTE_WORDS[1] + ".\n", 1),
        "zw.md": ("Plain\u200btext.\n", 1),
        "empty.md": ("  \n", 2),
    }

    def make(name: str, body: str, want: int) -> Callable[[], str | None]:
        def case() -> str | None:
            cfg = config()
            cfg["outbound"] = dict(cfg["outbound"], blocked_characters=[chr(0xA7)])
            tmp = pathlib.Path(tempfile.mkdtemp(prefix="audit_"))
            try:
                (tmp / name).write_text(body, encoding="utf-8")
                got = run(tmp / name, cfg, quiet=True)
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
            return None if got == want else "%s: exit %d, expected %d" % (name, got, want)
        return case

    return [("audit %s exits %d" % (name, want), make(name, body, want)) for name, (body, want) in cases.items()]


def selftest() -> int:
    fails = [msg for msg in (case() for _, case in selftest_cases()) if msg]
    for f in fails:
        print("FAIL:", f)
    print("[outbound_audit] selftest: %s (%d failure(s))" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.paths:
        ap.error("name at least one file")
    cfg = config()
    return max(run(pathlib.Path(p), cfg) for p in a.paths)


if __name__ == "__main__":
    sys.exit(main())
