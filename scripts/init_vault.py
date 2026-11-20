#!/usr/bin/env python3
"""Scaffold a starter vault: folders, root MOC, memory notes, templates.

Usage: python3 init_vault.py TARGET_DIR [--lang en|es] [--force]
Refuses to write into a non-empty folder unless --force (and never overwrites existing files).
"""
import argparse
from datetime import date
from pathlib import Path

LAYOUT = {
    "en": ["00_Inbox", "01_Projects", "02_Areas", "03_Reference", "04_Memory", "05_Logs", "MOCs", "_Archive", "_Templates"],
    "es": ["00_Bandeja", "01_Proyectos", "02_Areas", "03_Referencia", "04_Memoria", "05_Registros", "MOCs", "_Archivo", "_Plantillas"],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--lang", default="en", choices=["en", "es"])
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    root = Path(a.target).expanduser()
    if root.exists() and any(root.iterdir()) and not a.force:
        raise SystemExit(f"{root} is not empty. Use --force to add missing files only.")
    folders = LAYOUT[a.lang]
    today = date.today().isoformat()
    for f in folders:
        (root / f).mkdir(parents=True, exist_ok=True)
    skill = Path(__file__).resolve().parent.parent
    files = {
        "MOCs/MOC-Home.md": f"---\ntype: moc\ndescription: Root hub. Start here to find every other MOC.\ncreated: {today}\ntags: [moc]\n---\n\n# MOC: Home\n\n- [[MOC-Projects]]\n- [[MOC-Memory]]\n",
        "MOCs/MOC-Projects.md": f"---\ntype: moc\ndescription: Hub for active projects.\ncreated: {today}\ntags: [moc]\n---\n\n# MOC: Projects\n\n(Link each project note here.)\n",
        "MOCs/MOC-Memory.md": f"---\ntype: moc\ndescription: Hub for durable memory about the user: preferences and feedback.\ncreated: {today}\ntags: [moc]\n---\n\n# MOC: Memory\n\n- [[user-profile]]\n",
        f"{folders[4]}/user-profile.md": f"---\ntype: user\ndescription: Who the user is, role, how they like to work.\ncreated: {today}\ntags: [memory]\n---\n\n# User profile\n\nFill during onboarding. Part of [[MOC-Memory]].\n",
    }
    for rel, content in files.items():
        p = root / rel
        if not p.exists():
            p.write_text(content, encoding="utf-8")
    for t in ("note.md", "moc.md", "review-checklist.md"):
        src, dst = skill / "templates" / t, root / folders[-1] / t
        if src.exists() and not dst.exists():
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Vault scaffolded at {root.resolve()}")
    print("Next: python3 scripts/build_index.py", root)


if __name__ == "__main__":
    main()
