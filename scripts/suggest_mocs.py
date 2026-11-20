#!/usr/bin/env python3
"""Suggest new MOCs: themes (tags and title words) shared by 5+ notes that no MOC covers.

Usage: python3 suggest_mocs.py VAULT [--min-notes 5] [--json]
A note is 'covered' if any MOC links to it. Standard library only.
"""
import argparse, json, sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from _vault import iter_notes, parse_frontmatter, parse_list, tokens, links_of


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vault")
    ap.add_argument("--min-notes", type=int, default=5)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    root = Path(a.vault).expanduser().resolve()
    covered, notes = set(), {}
    for p in iter_notes(root):
        fm, body = parse_frontmatter(p.read_text(encoding="utf-8", errors="replace"))
        notes[p.stem] = (fm, body)
        if fm.get("type") == "moc" or p.stem.lower().startswith("moc"):
            covered.update(l.lower() for l in links_of(body))
    themes = defaultdict(set)
    for stem, (fm, body) in notes.items():
        if fm.get("type") == "moc" or stem.lower() in covered:
            continue
        for t in parse_list(fm.get("tags", "")):
            if t.lower() != "moc":
                themes[f"tag:{t.lower()}"].add(stem)
        for w in set(tokens(stem)):
            themes[f"word:{w}"].add(stem)
    out = [{"theme": k, "notes": sorted(v)} for k, v in themes.items() if len(v) >= a.min_notes]
    out.sort(key=lambda x: -len(x["notes"]))
    # drop themes that are subsets of a bigger kept theme
    kept = []
    for t in out:
        if not any(set(t["notes"]) <= set(k["notes"]) for k in kept):
            kept.append(t)
    if a.json:
        print(json.dumps(kept, indent=2))
    else:
        print(f"{len(kept)} MOC suggestion(s)")
        for t in kept:
            print(f"- {t['theme']} ({len(t['notes'])} notes): " + ", ".join(t["notes"][:8]))
    sys.exit(0)


if __name__ == "__main__":
    main()
