import json, subprocess, sys, tempfile, unittest
from pathlib import Path

S = Path(__file__).resolve().parent.parent / "scripts"
EX = Path(__file__).resolve().parent.parent / "examples" / "sample-vault"


def run(script, *args):
    r = subprocess.run([sys.executable, str(S / script), *map(str, args)], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def note(root, rel, body, fm="type: note\ncreated: 2026-01-01\n"):
    p = Path(root) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"---\n{fm}---\n\n{body}\n", encoding="utf-8")


class VaultTests(unittest.TestCase):
    def test_lint_detects_one_broken_link(self):
        code, out = run("vault_lint.py", EX)
        self.assertEqual(code, 1)
        self.assertIn("Missing Note", out)
        self.assertIn("Errors: 1", out)

    def test_lint_clean_vault(self):
        with tempfile.TemporaryDirectory() as d:
            note(d, "a.md", "see [[b]]")
            note(d, "b.md", "see [[a]]")
            code, out = run("vault_lint.py", d)
            self.assertEqual(code, 0, out)

    def test_infer_structure_json(self):
        code, out = run("infer_structure.py", EX)
        data = json.loads(out)
        self.assertEqual(data["notes"], 3)
        self.assertEqual(data["link_style"], "wikilinks")

    def test_index_puts_moc_first(self):
        with tempfile.TemporaryDirectory() as d:
            note(d, "zeta.md", "x", "type: reference\ndescription: z\ncreated: 2026-01-01\n")
            note(d, "MOC-A.md", "[[zeta]]", "type: moc\ndescription: hub\ncreated: 2026-01-01\n")
            run("build_index.py", d)
            lines = (Path(d) / "_INDEX.md").read_text().splitlines()
            notes = [l for l in lines if l.startswith("- ")]
            self.assertIn("MOC-A", notes[0])

    def test_init_vault_is_lint_clean(self):
        with tempfile.TemporaryDirectory() as d:
            v = Path(d) / "v"
            code, out = run("init_vault.py", v)
            self.assertEqual(code, 0, out)
            code, out = run("vault_lint.py", v)
            self.assertEqual(code, 0, out)

    def test_new_note_blocks_duplicate_and_links_moc(self):
        with tempfile.TemporaryDirectory() as d:
            note(d, "MOC-X.md", "hub", "type: moc\ncreated: 2026-01-01\n")
            code, out = run("new_note.py", d, "Camera Gear", "--type", "reference", "--description", "gear", "--moc", "MOC-X")
            self.assertEqual(code, 0, out)
            self.assertIn("[[Camera Gear]]", (Path(d) / "MOC-X.md").read_text())
            code, out = run("new_note.py", d, "Camera Gear")
            self.assertNotEqual(code, 0)
            code, out = run("new_note.py", d, "Camera Gears")
            self.assertNotEqual(code, 0)

    def test_duplicates_found(self):
        with tempfile.TemporaryDirectory() as d:
            body = "we agreed to ship the portfolio site redesign in march after the gallery page is complete and reviewed"
            note(d, "Meeting Notes.md", body)
            note(d, "Meeting Notes 2.md", body)
            code, out = run("find_duplicates.py", d)
            self.assertEqual(code, 1, out)

    def test_safe_rename_updates_links(self):
        with tempfile.TemporaryDirectory() as d:
            note(d, "Old.md", "x")
            note(d, "Ref.md", "see [[Old]] and [[Old#Head|alias]]")
            code, out = run("safe_rename.py", d, "Old", "New")
            self.assertTrue((Path(d) / "Old.md").exists(), "dry run must not rename")
            run("safe_rename.py", d, "Old", "New", "--apply")
            self.assertTrue((Path(d) / "New.md").exists())
            self.assertIn("[[New#Head|alias]]", (Path(d) / "Ref.md").read_text())
            code, out = run("vault_lint.py", d)
            self.assertNotIn("broken-link", out)

    def test_suggest_mocs(self):
        with tempfile.TemporaryDirectory() as d:
            for i in range(5):
                note(d, f"n{i}.md", "x", f"type: note\ncreated: 2026-01-01\ntags: [travel]\n")
            code, out = run("suggest_mocs.py", d)
            self.assertIn("tag:travel", out)


if __name__ == "__main__":
    unittest.main()
