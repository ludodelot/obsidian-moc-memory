# Obsidian MOC Memory

**An Agent Skill that turns an Obsidian vault into persistent memory for Claude Code, Codex, Cursor and other AI agents, organised with Maps of Content (MOCs).**

Your agent forgets everything between sessions. This skill gives it a second brain: a plain-markdown vault it can read, extend, link, review and prune, while respecting how *you* already organise notes.

## What it does

- **Learns your system first.** Scans an existing vault to detect folders, naming style, frontmatter, link style and MOCs, then confirms with you before changing anything.
- **MOC-first retrieval.** Reads the relevant Map of Content, follows its links, and only then searches. Cheaper and more accurate than scanning the whole vault.
- **Capture without duplicates.** "Remember this" updates an existing note or creates one with proper frontmatter and a MOC link.
- **Typed memory.** `user`, `feedback`, `project`, `reference`, `moc`, `log`.
- **Deterministic hygiene.** Scripts for broken wikilinks, orphan notes, missing frontmatter, duplicate titles, and a size-capped `_INDEX.md` for session start.
- **Weekly review.** A checklist to merge, archive and prune.
- **Private by design.** Local files only. Nothing is sent anywhere by the skill.

## Install

Claude Code (personal skill):

```bash
git clone https://github.com/ludodelot/obsidian-moc-memory ~/.claude/skills/obsidian-moc-memory
```

Other agents: copy the folder to wherever your agent loads skills, or point `AGENTS.md` to `SKILL.md`.

## Quick start

1. Tell the agent: *"Use obsidian-moc-memory on my vault at `~/Notes`."*
2. It runs `infer_structure.py`, shows what it found, and asks a few questions.
3. Say *"remember that I prefer short answers"* or *"what do my notes say about X?"*
4. Weekly: *"run my vault review."*

Try it on the bundled example:

```bash
python3 scripts/vault_lint.py examples/sample-vault
python3 scripts/infer_structure.py examples/sample-vault
python3 scripts/build_index.py examples/sample-vault
```

## Scripts (Python 3, standard library only)

| Script | Purpose |
|---|---|
| `scripts/infer_structure.py` | Detect folders, naming, frontmatter, link style, MOCs |
| `scripts/vault_lint.py` | Broken links, orphans, frontmatter, duplicates (exit 1 on errors) |
| `scripts/build_index.py` | Build `_INDEX.md`, MOCs first, under a size budget |

## Layout

```
SKILL.md      agent instructions
scripts/      deterministic checks
templates/    note, MOC, review checklist
references/   PKM methods, starter layout, failure modes
evals/        test cases
examples/     fake sample vault
```

## Related ideas

Obsidian second brain, Maps of Content (LYT), PARA, Zettelkasten, Johnny.Decimal, AI agent memory, Claude Code memory, CLAUDE.md, markdown knowledge base.

## Contributing

Issues and PRs welcome, especially eval cases and new vault-convention detectors.

## License

MIT. See [LICENSE](LICENSE).
