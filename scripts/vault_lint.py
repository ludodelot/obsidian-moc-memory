#!/usr/bin/env python3
"""Lint an Obsidian-style vault: broken wikilinks, orphans, frontmatter, duplicate titles.

Usage: python3 vault_lint.py VAULT [--json] [--require type,created] [--types user,feedback,...]
Exit code 1 if any error is found. Standard library only.
"""
import argparse, json, re, sys
from collections import defaultdict
from pathlib import Path

WIKILINK = re.compile(r"\[\[([^\]\|#]+)(?:#[^\]\|]*)?(?:\|[^\]]*)?\]\]")
CODE = re.compile(r"```.*?```|`[^`\n]*`", re.S)
DEFAULT_TYPES = {"user", "feedback", "project", "reference", "moc", "log", "note"}
SKIP_DIRS = {".git", ".obsidian", ".trash", "node_modules", "_Archive", "_Templates", "_Plantillas", "Templates"}


def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm = {}
    for line in text[3:end].strip().splitlines():
        if ":" in line and not line.startswith((" ", "-")):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, text[end + 4:]


def collect(root):
    notes = {}
    for p in root.rglob("*.md"):
        if any(part in SKIP_DIRS or part.startswith(".") for part in p.relative_to(root).parts[:-1]):
            continue
        notes[p] = p.read_text(encoding="utf-8", errors="replace")
    return notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vault")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--require", default="type,created")
    ap.add_argument("--types", default=",".join(sorted(DEFAULT_TYPES)))
    a = ap.parse_args()
    root = Path(a.vault).expanduser().resolve()
    required = [r for r in a.require.split(",") if r]
    types = set(a.types.split(","))
    notes = collect(root)

    by_stem = defaultdict(list)
    for p in notes:
        by_stem[p.stem.lower()].append(p)
    rel_index = {str(p.relative_to(root).with_suffix("")).lower(): p for p in notes}

    errors, warnings = [], []
    inbound = defaultdict(int)
    for p, text in notes.items():
        rel = str(p.relative_to(root))
        fm, body = parse_frontmatter(text)
        for key in required:
            if key not in fm:
                errors.append({"file": rel, "check": "frontmatter", "msg": f"missing '{key}'"})
        if fm.get("type") and fm["type"] not in types:
            warnings.append({"file": rel, "check": "type", "msg": f"unknown type '{fm['type']}'"})
        for m in WIKILINK.finditer(CODE.sub("", body)):
            target = m.group(1).strip().lower()
            if target.endswith(".md"):
                target = target[:-3]
            hit = rel_index.get(target)
            if hit is None:
                cands = by_stem.get(Path(target).name)
                if cands and len(cands) > 1:
                    warnings.append({"file": rel, "check": "ambiguous-link", "msg": f"[[{m.group(1)}]] matches {len(cands)} notes"})
                hit = cands[0] if cands else None
            if hit is None:
                errors.append({"file": rel, "check": "broken-link", "msg": f"[[{m.group(1)}]]"})
            elif hit != p:
                inbound[hit] += 1

    for stem, paths in by_stem.items():
        if len(paths) > 1:
            warnings.append({"file": ", ".join(str(x.relative_to(root)) for x in paths), "check": "duplicate-title", "msg": stem})
    for p, text in notes.items():
        fm, _ = parse_frontmatter(text)
        if inbound[p] == 0 and fm.get("type") != "moc" and not p.name.startswith(("_", "README", "MOC")):
            warnings.append({"file": str(p.relative_to(root)), "check": "orphan", "msg": "no inbound links"})

    report = {"notes": len(notes), "errors": errors, "warnings": warnings}
    if a.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Notes: {len(notes)}  Errors: {len(errors)}  Warnings: {len(warnings)}")
        for tag, items in (("ERROR", errors), ("WARN", warnings)):
            for i in items:
                print(f"[{tag}] {i['check']}: {i['file']}: {i['msg']}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
