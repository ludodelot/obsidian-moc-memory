#!/usr/bin/env python3
"""Create a note safely: frontmatter, duplicate guard, optional MOC link.

Usage: python3 new_note.py VAULT "Title" --type feedback --description "..." [--folder 04_Memory]
       [--tags a,b] [--moc MOC-Memory] [--body "text"] [--force]
Refuses when a note with the same or very similar title exists (use --force to override).
"""
import argparse, difflib, re, sys
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from _vault import iter_notes

TYPES = {"user", "feedback", "project", "reference", "moc", "log", "note"}


def slug_ok(title):
    return re.sub(r'[\\/:*?"<>|#^\[\]]', "-", title).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vault")
    ap.add_argument("title")
    ap.add_argument("--type", default="note", choices=sorted(TYPES))
    ap.add_argument("--description", default="")
    ap.add_argument("--folder", default="")
    ap.add_argument("--tags", default="")
    ap.add_argument("--moc", default="")
    ap.add_argument("--body", default="")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    root = Path(a.vault).expanduser().resolve()
    name = slug_ok(a.title)
    existing = {p.stem.lower(): p for p in iter_notes(root)}
    if not a.force:
        if name.lower() in existing:
            sys.exit(f"Exists: {existing[name.lower()].relative_to(root)}. Update it instead.")
        close = difflib.get_close_matches(name.lower(), list(existing), n=3, cutoff=0.82)
        if close:
            sys.exit("Very similar note(s): " + ", ".join(str(existing[c].relative_to(root)) for c in close) + ". Update one, or use --force.")
    folder = root / a.folder
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{name}.md"
    tags = [t.strip() for t in a.tags.split(",") if t.strip()]
    fm = f"---\ntype: {a.type}\ndescription: {a.description}\ncreated: {date.today().isoformat()}\ntags: [{', '.join(tags)}]\n---\n\n# {a.title}\n\n{a.body}\n"
    path.write_text(fm, encoding="utf-8")
    msg = f"Created {path.relative_to(root)}"
    if a.moc:
        moc = existing.get(a.moc.lower()) or next((p for p in iter_notes(root) if p.stem.lower() == a.moc.lower()), None)
        if moc is None:
            msg += f" (MOC '{a.moc}' not found: link it manually)"
        else:
            text = moc.read_text(encoding="utf-8")
            line = f"- [[{name}]] — {a.description}".rstrip(" —")
            if f"[[{name}]]" not in text:
                moc.write_text(text.rstrip("\n") + "\n" + line + "\n", encoding="utf-8")
            msg += f" and linked from {moc.relative_to(root)}"
    print(msg)


if __name__ == "__main__":
    main()
