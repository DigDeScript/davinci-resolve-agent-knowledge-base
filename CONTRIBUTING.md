# Contributing verified DaVinci Resolve knowledge

This is a **public** agent-first reference library. Proposed discoveries are welcome, but no proposal is treated as verified merely because a submitting agent reports success.

## Proposal process

1. Read [GUIDE.md](GUIDE.md) and locate the existing topic in [modules/INDEX.md](modules/INDEX.md). Check [known traps](modules/known-traps.md) to avoid duplicating a documented result.
2. Work on a fresh feature branch from the latest `main`, e.g. `proposal/word-highlight-recolor` or `trap/audio-ripple-delete`.
3. Make the smallest relevant documentation/tool/test change. Preserve previous evidence and other agents' work; never force-push `main`.
4. Supply a PR description using [the template](.github/PULL_REQUEST_TEMPLATE.md), including exact Resolve version, circumstances, reproduction steps, observations, negative/uncertain results and validation coverage.
5. Refresh `MANIFEST.json` with `python tools/validate_library.py --write-manifest`, then run `python tools/validate_library.py --check` and `python -m unittest discover -s tests -p 'test_*.py'`.
6. Push the *proposal branch* and open a Pull Request targeting `main`. Do not self-approve or self-merge.

**When no repository write access exists:** submit a PR-ready report to the task owner instead. Do not interrupt the editing task solely to demand GitHub access.

## Evidence labels

- `locally tested`: demonstrated under clearly specified conditions, with test scope and limits.
- `externally documented`: cited declaration/example, without local reproduction.
- `experimental`: promising unverified approach needing an actual task test.
- `observed to fail`: reproducible adverse behavior in a named environment.
- `unverified report`: new field observation awaiting independent reproduction.

Unverified contributions may be submitted as proposals, **but must not be written as unconditional verified instructions**. Confirmed failures belong in [`modules/known-traps.md`](modules/known-traps.md); successful validated procedures belong in a corresponding topic module. If findings are unresolved, keep them in the PR report or a clearly labelled evidence note until review.

## Independent review

The owner instructs a separate validation agent to review the PR, perform targeted Resolve tests where possible and document the outcome. Offline CI checks syntax, file links, manifest checksums and utility tests; **CI does not certify Resolve integration, human-visible aesthetics or audio quality**. A reviewer can request changes, reject the proposal or recommend approval, citing reproduction details. Only the authorized owner/reviewer merges to `main` after checks.

Do not merge code or a detailed method if evidence is insufficient for its claimed status. Failed tests can still justify a carefully qualified known-trap entry. Preserve the source of contradictory observations.

## Public-repository safety

Never publish passwords, tokens, personally identifiable information, private source media, proprietary editing projects or client-derived material without permission. Keep screenshots/audio/video out of routine contributions unless explicitly cleared. All reproducible examples should use synthetic or otherwise shareable material. `main` is reviewed, **not a warranty across Resolve versions**.
