# Capability index — need → method → known traps

[Start here](../GUIDE.md) · [Agent usage and PR rules](../AGENTS.md) · [Known traps](known-traps.md)

Use this index **after** identifying what the current task requires. Read only relevant modules. Follow the trap link *before* applying a selected method; check the evidence and installed Resolve API when behavior varies by version. A missing entry is not proof that an action is safe or impossible.

| Agent needs to… | Find candidate methods | Verify / avoid |
|---|---|---|
| Connect to Resolve, protect originals, inspect state | [Setup and safety](setup-and-safety.md), [Resolve 21.2](resolve-21.2.md) | [Safety and API traps](known-traps.md), [recorded trials](../evidence/resolve-21.2.0.5.md) |
| Import media, create a timeline, map timebases/frames | [Timeline and media](timeline-and-media.md) | [Frame/mark/insert traps](known-traps.md) |
| Move or trim linked picture and audio without sync drift | [AV pairing and sync](av-sync-and-trim.md) | [Sync and trim traps](known-traps.md) |
| Plan content-led or transcript-led cuts | [Transcript-driven editing](transcript-driven-editing.md), [editing standards](editing-standards.md) | [Word timing, missing frames, inappropriate B-roll](known-traps.md) |
| Detect pauses, estimate audio levels, build non-destructive cut plans | [Audio analysis/edit plans](audio-analysis-and-edit-plans.md), [audio and color](audio-and-color.md) | [Silence deletion limits](resolve-21.2.md), [known traps](known-traps.md) |
| Create native editable titles and subtitles | [Native Text+](native-text-plus.md), [Word Highlight](word-highlight.md) | [Shading/Fusion/DRT traps](known-traps.md) |
| Animate Fusion tools, splines or macros | [Fusion and animation](fusion-and-animation.md) | [Graph and keyframe traps](known-traps.md) |
| Isolate foregrounds, composite masks or depth effects | [Masking and depth](masking-and-depth.md) | [Matte/DepthMap/Magic Mask traps](known-traps.md) |
| Balance audio/color or understand limitations | [Audio and color](audio-and-color.md), [Resolve 21.2](resolve-21.2.md) | [Ducker and native API limits](known-traps.md) |
| Design better audience engagement / promotional edits | [Audience engagement](audience-engagement.md), [editing standards](editing-standards.md) | Client brief; [editorial traps](known-traps.md) |
| Render, inspect frames, compare saved-state revisions | [Render and QA](render-and-qa.md), [tool catalog](../tools/README.md) | [QA guidance](../workflows/quality-check.md), [known traps](known-traps.md) |
| Determine evidence confidence / research unknown behavior | [Evidence and research](evidence-and-research.md), [current test record](../evidence/resolve-21.2.0.5.md) | [Contribution protocol](../CONTRIBUTING.md) |

## If no matching method exists

Design a feasible method; check [known traps](known-traps.md), installed API declarations and project safety; run a bounded practical test; capture factual findings. If the technique is reusable, submit a **Pull Request** following [CONTRIBUTING.md](../CONTRIBUTING.md) rather than editing `main` directly.

## Inherited method status

Previous versions' specialist recipes and original evidence labels remain in place. Later build-specific evidence may qualify older claims; prefer a direct observation in the same environment over an untested extrapolation. The library does not promise that all historical recipes have been retested on Resolve 21.2.
