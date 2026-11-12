# Instructions for AI agents working with this repository

This public repository is an **agent-consumable knowledge base** for DaVinci Resolve, not a generic task checklist. Start with [GUIDE.md](GUIDE.md), identify the current task's needs and follow the [capability index](modules/INDEX.md).

## Editing agent: read, apply, learn

1. Treat the client's goal, permissions and creative requirements as authoritative for that editing task.
2. Search for a relevant candidate method, then check [known traps](modules/known-traps.md), compatibility notes and available evidence **before applying it**.
3. If needed, develop an alternative and test it on appropriate isolated/safe material. Protect original projects and source media.
4. Record factual outcomes: Resolve build, source/initial conditions, exact API or actions, observed outputs, read-back/save/reopen results, visual/audio review coverage and remaining uncertainties.
5. If a new reusable method or failure case arises, prepare a focused change on a **new branch** and open a **Pull Request against `main`** following [CONTRIBUTING.md](CONTRIBUTING.md), **only if the task grants write permission and the environment exposes Git/GitHub access**.
6. Never push to `main`, approve/merge your own PR, delete existing verified evidence or silently convert unverified hypotheses into established recommendations. If unavailable or unauthorized to contribute, include a PR-ready finding in the final task report instead.

Ordinary editing-task results do **not** require a PR when no reusable lesson was learned. The task's actual editing deliverable remains the primary goal.

## Validation agent: separate reviewer

Operate only on explicit owner/reviewer instruction. Inspect a PR's scope and evidence; reproduce the claim in an appropriate Resolve environment where feasible; distinguish direct reproduction, offline validation, inability to test and contradictory evidence. Explain what was checked and what was not. Request changes or reject unsupported claims; approve only at the evidence level actually established. Merge to `main` **only with explicit repository-owner authorization** and after required repository checks. Avoid making unrelated edits while reviewing another agent's PR.

## Evidence discipline

- Tag claims as `locally tested`, `externally documented`, `experimental`, `observed to fail`, or `unverified report` with context. A successful unit test is not proof of good audiovisual output.
- Do not add client media, personal data, access tokens, private project files or proprietary renders to this **public** repo. Use anonymized minimal traces, descriptions and reproducible procedures.
- Preserve existing recipes and evidence; if new evidence contradicts them, explain the difference and propose a scoped correction.
- Keep [MANIFEST.json](MANIFEST.json) current with `python tools/validate_library.py --write-manifest` whenever tracked library files change; run `python tools/validate_library.py --check` and Python tests before requesting review.
- GitHub access is not required to *use* the knowledge base. Lack of permission or an unavailable integration is not permission to bypass the review process.
