"""Shared helpers for obsidian-moc-memory scripts. Standard library only."""
import re
from pathlib import Path

SKIP_DIRS = {".git", ".obsidian", ".trash", "node_modules", "_Archive", "_Templates", "_Plantillas", "Templates"}
WIKILINK = re.compile(r"\[\[([^\]\|#]+)(?:#[^\]\|]*)?(?:\|[^\]]*)?\]\]")
CODE = re.compile(r"```.*?```|`[^`\n]*`", re.S)
STOPWORDS = set("the a an and or of to in for with on at by from is are be this that it its my our your note notes about new old".split())


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


def parse_list(value):
    """'[a, b]' or 'a, b' -> ['a','b']"""
    v = (value or "").strip().strip("[]")
    return [x.strip().strip("'\"#") for x in v.split(",") if x.strip()]


def iter_notes(root):
    root = Path(root).expanduser().resolve()
    for p in sorted(root.rglob("*.md")):
        rel = p.relative_to(root)
        if any(part in SKIP_DIRS or part.startswith(".") for part in rel.parts[:-1]):
            continue
        yield p


def tokens(text):
    return [t for t in re.findall(r"[a-z0-9][a-z0-9\-']+", text.lower()) if t not in STOPWORDS and len(t) > 2]


def links_of(body):
    return [m.group(1).strip() for m in WIKILINK.finditer(CODE.sub("", body))]
