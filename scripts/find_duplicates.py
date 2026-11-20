#!/usr/bin/env python3
"""Find likely duplicate notes by title similarity and content overlap.

Usage: python3 find_duplicates.py VAULT [--title-cutoff 0.85] [--content-cutoff 0.6] [--json]
Content overlap = Jaccard similarity of word 3-gram shingles. Standard library only.
"""
import argparse, difflib, json, sys
from itertools import combinations
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from _vault import iter_notes, parse_frontmatter, tokens


def shingles(text, n=3):
    t = tokens(text)
    return {" ".join(t[i:i + n]) for i in range(max(len(t) - n + 1, 0))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vault")
    ap.add_argument("--title-cutoff", type=float, default=0.85)
    ap.add_argument("--content-cutoff", type=float, default=0.6)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    root = Path(a.vault).expanduser().resolve()
    data = []
    for p in iter_notes(root):
        _, body = parse_frontmatter(p.read_text(encoding="utf-8", errors="replace"))
        data.append((p, p.stem.lower(), shingles(body)))
    found = []
    for (p1, t1, s1), (p2, t2, s2) in combinations(data, 2):
        tr = difflib.SequenceMatcher(None, t1, t2).ratio()
        cr = len(s1 & s2) / len(s1 | s2) if s1 and s2 else 0.0
        if tr >= a.title_cutoff or cr >= a.content_cutoff:
            found.append({"a": str(p1.relative_to(root)), "b": str(p2.relative_to(root)), "title_similarity": round(tr, 2), "content_overlap": round(cr, 2)})
    if a.json:
        print(json.dumps(found, indent=2))
    else:
        print(f"{len(found)} likely duplicate pair(s)")
        for f in found:
            print(f"- {f['a']}  <->  {f['b']}  (title {f['title_similarity']}, content {f['content_overlap']})")
    sys.exit(1 if found else 0)


if __name__ == "__main__":
    main()
