#!/usr/bin/env python3
"""Rename a note and rewrite every [[wikilink]] to it. Dry run by default.

Usage: python3 safe_rename.py VAULT "Old Title" "New Title" [--apply]
Preserves #heading and |alias parts. Aborts if the new name already exists or the old name is ambiguous.
"""
import argparse, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from _vault import iter_notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vault")
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    root = Path(a.vault).expanduser().resolve()
    notes = list(iter_notes(root))
    olds = [p for p in notes if p.stem == a.old]
    if len(olds) != 1:
        sys.exit(f"Expected exactly one note named '{a.old}', found {len(olds)}.")
    if any(p.stem.lower() == a.new.lower() for p in notes):
        sys.exit(f"A note named '{a.new}' already exists.")
    pat = re.compile(r"\[\[" + re.escape(a.old) + r"((?:#[^\]\|]*)?(?:\|[^\]]*)?)\]\]")
    changes = []
    for p in notes:
        text = p.read_text(encoding="utf-8")
        new_text, n = pat.subn(lambda m: f"[[{a.new}{m.group(1)}]]", text)
        if n:
            changes.append((p, new_text, n))
    print(f"{olds[0].relative_to(root)} -> {a.new}.md")
    for p, _, n in changes:
        print(f"  {n} link(s) updated in {p.relative_to(root)}")
    if not a.apply:
        print("Dry run. Re-run with --apply to write changes (back up or commit first).")
        return
    for p, t, _ in changes:
        p.write_text(t, encoding="utf-8")
    olds[0].rename(olds[0].with_name(a.new + ".md"))
    print("Applied.")


if __name__ == "__main__":
    main()
