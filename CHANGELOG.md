# Proposed: title-promo lessons and portable validation (2026-11-14)

- Add bounded Studio 21.2.0.6 font/style and published-group-output observations, reproduction steps and independent-review limits.
- Extend promotional guidance with host-app identification, user-confirmed offer, registration/download steps and readable end-card timing.
- Check Python syntax in memory, removing the offline validator's hard-coded `/tmp` bytecode writes.

---

# Resolve Agent 1.9

Released 2026-11-12. **Knowledge management and GitHub workflow update** of v1.8; no new live Resolve integration validation. Latest recorded Resolve test build remains 21.2.0.5.

- `GUIDE.md` and `modules/INDEX.md` now route by *task need → candidate method → relevant known traps*, with fallbacks and evidence-status checks.
- Added `AGENTS.md` and `CONTRIBUTING.md`: editing agents propose reusable discoveries in PRs, a separately instructed validation agent reproduces and reviews, and only an authorized maintainer merges into `main`.
- Added GitHub PR template and read-only CI validation workflow for offline unit tests, Python syntax, local links and manifest integrity. CI is **not** equivalent to Resolve/video/audio integration validation.
- Added `tools/validate_library.py` and `.gitignore`; updated manifest and root `README.md`. Historic detailed recipes/tools/test evidence are preserved.
- Public repository precautions: no client source footage, private project files, access credentials or personal data in contributions.

---

# Resolve Agent 1.8

Released 2026-11-06. **Documentation-only update** of v1.7; latest recorded Resolve integration environment remains Studio 21.2.0.5.

- `GUIDE.md` now explicitly describes the package as a **reference library**, not a mandatory workflow or a creative brief. Its former six-stage normal path remains available in `workflows/editing.md` as an optional example.
- New `modules/audience-engagement.md`: conditional approaches for promotional communication, viewer orientation, evidence-led demonstration, pacing, B-roll, captions, sound, endings and audience feedback. No forced hook formula, fixed shot interval, marketing claim or CTA.
- `modules/INDEX.md` links to the new topic. `README_LT.md` explains library use.
- Existing `tools/`, `assets/`, local tests, evidence files and detailed Resolve API references remain byte-for-byte unchanged. This release is **not** a new integration-test result.

---

# Resolve Agent 1.7

Released 2026-11-06. Current integration trials: Studio 21.2.0.5 on 2026-11-05.

## Information structure

- `GUIDE.md` is the short entry point. The extended workflow is in `workflows/editing.md`, completion checks in `workflows/quality-check.md`, specialist references in `modules/INDEX.md`.
- New current-version reference: `modules/resolve-21.2.md`. Earlier module examples are explicitly labelled as historical evidence and link to current dictionary API forms.
- The original native Word Highlight asset, two existing utilities and v1.2 archive remain included. The package contains no personal source media, models or third-party MCP dependency.

## Working additions

- `tools/resolve_inspect.py`: native state capture and field-by-field comparison; read errors cannot pass verification; no project mutation.
- `tools/review_frames.py`: native labelled source/timeline grids, cut-edge offsets and state-bound evidence without moving the playhead.
- Seven offline tests plus recorded live integration trials. Evidence separates declared APIs, real execution, visual inspection and unresolved behavior.
- Newly verified clip loudness analysis, paired trim/move, audio property persistence, auto color, native grid/ROI export and playback-FPS setter.

## Corrections to earlier claims

- `RippleDeleteSilence` is declared, including in the installed 21.1.2 changelog. Its API existence was previously understated. Current correctness tests failed, so it remains experimental for a different, evidenced reason.
- `GetProperties`/`SetProperties` and `GetSettings`/`SetSettings` are the current declared forms. Older singular aliases are not assumed.
- Video `SetFades` persistence failure was independently reproduced on 21.2.0.5. This is not generalized to all fades or all versions.
- Native clip analysis is not final-mix analysis, frame grids are not playback, and matching AV structure is not perceptual sync proof.

## Migration

Use this folder as a standalone library and point the next agent to `GUIDE.md`. No installation or replacement of the previous version is required. Run tool commands from this package root and write task artifacts to a separate `work` directory. Reuse only relevant recipes; do not ask an editing agent to read the entire historical archive.

Existing detailed modules preserve valuable earlier evidence. Where a historical recipe and the current-version module disagree about API access or observed 21.2 behavior, use the current-version module and installed declarations. Historical archive text is not a current compatibility promise.
