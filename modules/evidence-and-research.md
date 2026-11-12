# Evidence provenance, unresolved API questions and change reporting

> **21.2 compatibility:** this module preserves earlier recipes and evidence. For current signatures, newly tested operations and restrictions, read [Resolve 21.2](resolve-21.2.md). Older `GetProperty`/`SetProperty` and `GetSetting`/`SetSetting` examples require the current dictionary forms.


> [Back to GUIDE.md](../GUIDE.md) | Evidence keys and general safety: [setup-and-safety.md](setup-and-safety.md)

## Report new findings separately, not as a long appendix

After each new editing task, deliver a separate `RESOLVE_API_FINDINGS.md` with:
- **Newly verified operation:** Resolve build, exact API call/arguments, initial conditions, result/read-back, save/reopen outcome and human editability.
- **Unresolved operation:** the smallest concrete test that would distinguish competing explanations; do not turn a misunderstanding into an API limitation.
- **Proposed guide change:** only a reusable recipe or a short **X → Y → Z** warning, not a chronological debugging diary.

**Open research priorities:** (1) manually dragging/editing Fusion Spline keyframes; (2) Magic Mask stroke/tracking automation and finer DepthMap mattes; (3) native Fairlight and Color page automation, **including native A2 Ducker controlled by A1**; (4) safe precision trim/ripple without damaging other clips; (5) stable recovery, temporal matte quality and compositing verification; (6) Text+ Layout Circle/Path and other Blending modes; (7) programmatic individual subtitle-word timing edits, detailed subtitle styling beyond tested RGB channels and GUI/MCP controls.

**Provenance / follow-up references:** `RESOLVE_AGENT_GUIDE_feedback_1.md`, `STARGATE_V3_API_FINDINGS.md`, `TEXTPLUS_INSPECTOR_ANIMATION_V4.md`, `Resolve_Agent_Playbook_v0.1.1.md`, `MONTAVIMO_PATIRTIS_IR_PATOBULINIMAI.md`, `RESOLVE_AGENT_GUIDE_feedback_v1.2.md`, the user-supplied November 2026 `rebuild_shading_samples.py` code and screenshots, the prior `darbas-prie-efekto_20261027_0258.json`, and selected scripts inside `resolve agent roadmap.zip`. For API verification use the **installed** `Developer/Scripting/README.md`, `DaVinciResolveScript.pyi`, Fusion scripting references, and the active MCP tool descriptions. Public background references: https://wiki.dvresolve.com/developer-docs/scripting-api and https://documents.blackmagicdesign.com/UserManuals/Fusion8_Scripting_Guide.pdf.

*This is an operational guide, not a universal executable script. Every result remains conditional on the installed Resolve version and actual state/visual read-back.*

**New evidence (2026-11-02):** `WH_Before_Subtitles_Test.drt` supplied by user; Word Highlight holder extraction, two tested RGB groups, corrected DRT embedded length header, success on an effect-free timeline and on an empty native subtitle track before caption generation. See [word-highlight.md](word-highlight.md).

## New integration evidence — 2026-11-02 [R, user + agent report]

A fresh agent conversation used this guide in a new project (`word highlight test2`) to produce a 2:57.6 / 24 fps edit from an 18:56.5 source, 15 editorial segments and 85 native English captions. The agent reported two successful Word Highlight DRT workflow passes with different specified colors, intact Fusion data, MP4 decoding and subtitle render; the user said the overall edit was good with some tolerable defects. This is **production evidence for the tested Resolve Studio 21.1.2.10 environment**, not universal compatibility, perfect join timing, or proof of human-reviewed full audio. The agent specifically identified opportunities to improve transcript-based segmentation, B-roll cover selection, cut-frame QA and output burn-in settings. See [Transcript-driven editing](transcript-driven-editing.md).

## Additional editing task evidence — 2026-11-02 [R, agent + user]

A second independent agent (`GPT-6 Sol`, user-reported) assembled a 49.5-second, 1080×1920, 24 fps walk/personal reel from 14 picture/still segments and 10 dialogue segments. It preserved independent music and source timeline, resolved several one-frame picture gaps and corrected an initially excessive 3.16 phone-media zoom after inspecting Resolve-exported stills. The agent reported that a dictionary-style `ImportMedia` batch returned `None`, and automatic speech recognition chose an incorrect language; explicit language verification is now a preflight rule. **A2 Track FX Ducker was not installed** because UI capture/control failed and a validated public scripting method was not found; this remains an open research problem, not a completed automation. The **user revised shot selections and speech edits extensively**, judging the personal reel only moderately successful. This supports task-type-specific editorial workflow and human review; it does **not** prove the agent can consistently choose the strongest personal footage or guarantee natural speech cuts.

## External repository comparison — 2026-11-04 (v1.6)

These are **external references**, not evidence of local API support or shipped dependencies:

- `samuelgursky/davinci-resolve-mcp`: source-safe FFmpeg silence analysis; guarded editing plans and transcript/media analysis. https://github.com/samuelgursky/davinci-resolve-mcp
- `CiprianSpiridon/davinci-resolve-mcp`: offline `.drp`/`.drt` project inspection, project-state differences and `ebur128` LUFS/dBTP/LRA monitoring. https://github.com/CiprianSpiridon/davinci-resolve-mcp
- `tmoroney/auto-subs`: Fusion spline, `.setting` macro, published controls and optional transcript/word timing alignment. https://github.com/tmoroney/auto-subs
- `AdamGarceau/resolve-toolkit`: transcript-driven tightening, speaker-oriented edits, animated title assets, JSONL shot/B-roll catalog reference. https://github.com/AdamGarceau/resolve-toolkit
- `odaiouattara0022-del/davinci-resolve-skill`: source-file FFmpeg-assisted silence analysis and basic Resolve scripting recipes. https://github.com/odaiouattara0022-del/davinci-resolve-skill

The v1.6 additions are **reference descriptions and one read-only analysis utility**. No external MCP servers were installed or bundled. Historical status: direct `Remove Silence` was unresolved. The 1.7 update now documents and tests it, with failing correctness results; see [current evidence](../evidence/resolve-21.2.0.5.md). Ducker, existing-track recoloring and other untested Fusion operations remain unresolved.
