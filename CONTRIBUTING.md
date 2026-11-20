# Contributing to Obsidian MOC Memory

- Scripts use only the Python standard library. Keep it that way, or make the extra dependency optional with a clear message.
- Add a unit test in `tests/` for every behaviour change, and an eval row in `evals/evals.md` for agent-level behaviour.
- Run `python3 -m unittest discover -s tests` before opening a PR.
- Never commit personal data. Examples must use fake data.
- Keep `SKILL.md` concise: details belong in `references/`.
