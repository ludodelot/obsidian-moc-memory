# Failure modes and mitigations

| Problem | Mitigation |
|---|---|
| Note sprawl | Capture to inbox, review weekly, MOC per 5+ notes |
| Duplicates | Search index before creating; `vault_lint.py` flags duplicate titles |
| Stale facts | Absolute dates in project notes; review checklist step 4 |
| Index bloat | `build_index.py --max-bytes`, MOCs first, archive old notes |
| Hallucinated links | Only link to notes that exist; lint fails on broken links |
| Over-linking | Link only where the relation helps retrieval; hubs carry the rest |
| Overwriting user style | Run `infer_structure.py`, confirm before migrating |
