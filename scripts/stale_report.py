#!/usr/bin/env python3
"""List notes that may be stale: project/log/feedback notes not modified for N days.

Usage: python3 stale_report.py VAULT [--days 90] [--types project,log]
Uses file modification time. Output is a review list, not an action. Standard library only.
"""
import argparse, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from _vault import iter_notes, parse_frontmatter


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vault")
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--types", default="project,log")
    a = ap.parse_args()
    root = Path(a.vault).expanduser().resolve()
    types = set(a.types.split(","))
    cutoff = time.time() - a.days * 86400
    rows = []
    for p in iter_notes(root):
        fm, _ = parse_frontmatter(p.read_text(encoding="utf-8", errors="replace"))
        if fm.get("type") in types and p.stat().st_mtime < cutoff:
            rows.append((int((time.time() - p.stat().st_mtime) / 86400), str(p.relative_to(root)), fm.get("type")))
    rows.sort(reverse=True)
    print(f"{len(rows)} possibly stale note(s) (> {a.days} days)")
    for d, rel, t in rows:
        print(f"- {rel} ({t}, {d} days)")


if __name__ == "__main__":
    main()
