#!/usr/bin/env python3
"""Infer how a user organises an existing vault: folders, naming, frontmatter, links, MOCs.

Usage: python3 infer_structure.py VAULT   (prints JSON). Standard library only.
"""
import json, re, sys
from collections import Counter
from pathlib import Path

SKIP = {".git", ".obsidian", ".trash", "node_modules", "_Templates", "_Plantillas", "Templates"}
NAMING = {
    "date-prefix (YYYY-MM-DD)": re.compile(r"^\d{4}-\d{2}-\d{2}"),
    "numeric-prefix (Johnny.Decimal/ordered)": re.compile(r"^\d{1,3}[ _.-]"),
    "kebab-case": re.compile(r"^[a-z0-9]+(-[a-z0-9]+)+$"),
    "snake_case": re.compile(r"^[A-Za-z0-9]+(_[A-Za-z0-9]+)+$"),
    "spaces/Title Case": re.compile(r"^[A-Z0-9][^_]* [^_]*$"),
}


def main():
    root = Path(sys.argv[1]).expanduser().resolve()
    files = [p for p in root.rglob("*.md") if not any(x in SKIP or x.startswith(".") for x in p.relative_to(root).parts[:-1])]
    folders = Counter(p.relative_to(root).parts[0] for p in files if len(p.relative_to(root).parts) > 1)
    naming, fm_keys, types, tags = Counter(), Counter(), Counter(), Counter()
    wiki = md_links = with_fm = 0
    mocs = []
    for p in files:
        for label, rx in NAMING.items():
            if rx.search(p.stem):
                naming[label] += 1
        text = p.read_text(encoding="utf-8", errors="replace")
        wiki += len(re.findall(r"\[\[[^\]]+\]\]", text))
        md_links += len(re.findall(r"\]\((?!http)[^)]+\.md\)", text))
        if text.startswith("---") and "\n---" in text[3:]:
            with_fm += 1
            head = text[3:text.find("\n---", 3)]
            for line in head.splitlines():
                if ":" in line and not line.startswith((" ", "-")):
                    k, v = line.split(":", 1)
                    fm_keys[k.strip()] += 1
                    if k.strip() == "type":
                        types[v.strip()] += 1
        tags.update(re.findall(r"(?<!\w)#([A-Za-z][\w/-]+)", text))
        if "moc" in p.stem.lower() or re.search(r"^type:\s*moc", text, re.M):
            mocs.append(str(p.relative_to(root)))
    n = max(len(files), 1)
    out = {
        "notes": len(files),
        "top_folders": folders.most_common(15),
        "naming_patterns": {k: f"{v}/{len(files)}" for k, v in naming.most_common()},
        "frontmatter_coverage": f"{with_fm}/{len(files)}",
        "frontmatter_keys": fm_keys.most_common(12),
        "note_types": types.most_common(),
        "link_style": "wikilinks" if wiki >= md_links else "markdown-links",
        "wikilinks": wiki, "markdown_links": md_links,
        "top_tags": tags.most_common(10),
        "mocs": mocs[:30],
        "dominant_naming": (naming.most_common(1) or [("none", 0)])[0][0] if naming and naming.most_common(1)[0][1] / n > 0.4 else "mixed/none",
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
