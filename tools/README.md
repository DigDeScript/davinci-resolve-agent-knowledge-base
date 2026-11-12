# Small tools, ready to use

> [Start page](../GUIDE.md) · [Current API](../modules/resolve-21.2.md)

Run the commands from the package root. The new helpers use Python's standard library and the installed Resolve bridge; no pip installation is needed. They never edit, save, close or switch a Resolve project. Output paths must be new. Windows / Python 3.13 / Studio 21.2.0.5 were tested; other systems can set `RESOLVE_SCRIPT_API` to their installed `Developer/Scripting` directory but have not been validated here.

## 1. Know the real current state

```text
python tools/resolve_inspect.py snapshot --output work/before.json
```

Read the project/timeline IDs in the JSON. Optional `--timeline-id "EXACT_ID"` limits timeline capture; Media Pool and project settings are still included. The report contains fractional edges, source mapping, linked IDs, speed, clip properties (including gain), fades, transition properties, settings, markers and media paths. It explicitly excludes full Fusion/Color graphs, automation curves and perceptual checks. Inspect `read_errors`; unavailable data cannot pass verification.

After your authorized edits and a protected save/reopen, capture again:

```text
python tools/resolve_inspect.py snapshot --output work/after.json
python tools/resolve_inspect.py compare work/before.json work/after.json --output work/comparison.json
```

For persistence specifically, take `before` **after editing and immediately before save/reopen**, then `after` after reacquiring the reopened project. Otherwise the diff will correctly include the intentional edit too. Use the same capture scope. The comparison is field-by-field, without numerical tolerance; it does not reopen anything or automatically repair differences. `Usage` count refreshes are separate observations. Metadata changes such as `0x0` → resolved dimensions are still reported; interpret them rather than hiding them.

Exit codes: `0` = capture without read errors / equal captured state; `2` = incomplete capture or different/incomplete comparison; `1` = execution error. Equality refers only to captured fields. It is not a completed film-quality check.

## 2. Review native source or timeline frames

Replace `EXACT_ID` with an ID read from the snapshot, keeping the quotes:

```text
python tools/review_frames.py --timeline-id "EXACT_ID" --cuts --output-dir work/cut_review
python tools/review_frames.py --timeline-id "EXACT_ID" --frames 0,60,120 --output-dir work/timeline_samples
python tools/review_frames.py --media-id "EXACT_ID" --frames 0,60,120 --output-dir work/source_samples
```

`--cuts` exports both actual edges of successive video clips on `--track 1` by default. It ignores transition items and preserves actual edge locations even around a gap. It does not inspect upper-track overlays, generators, the full shot, opening/closing or audio by itself. Use explicit `--frames` for those. All offsets are **relative to the selected object**, not absolute timeline frame numbers; MediaPool source offsets and timeline offsets can have different timebases.

Each output directory contains JPEG grids and `review.json`: target state, exact offsets, export results, state hash and playhead checks. Defaults: six frames per sheet, maximum whole-sheet dimension 1600. Inspect images through an available image viewer; exported files remain “inspection pending” until actually viewed. Do not label them as playback or listening evidence. Timeline/source paths and IDs are included in the JSON; handle the report as project data.

The tested tool exported all 78 edge frames for 39 joins in 13 grids without changing the captured timeline state or playhead. The source mode was separately exercised.

## 3. Existing utilities

| Tool | Use | Limit |
|---|---|---|
| [silence_probe.py](silence_probe.py) | FFmpeg low-level interval candidates, JSON output | Not per-channel edge certification, semantic editing or timeline mutation |
| [word_highlight.py](word_highlight.py) | Offline native subtitle DRT holder installation / RGB editing | Original 21.1.2 format evidence; 21.2 import round-trip not retested |

```text
python tools/silence_probe.py "SOURCE.mp4" --noise-db -80 --min-silence 0.03 --output work/quiet_candidates.json
python tools/word_highlight.py --help
```

The short-interval silence example is a diagnostic starting point, not a preset for speech cuts. Check the actual source, channel behavior and parameters. These two inherited tools keep their existing overwrite behavior; choose new filenames yourself. The two **new** tools refuse overwriting outputs.

Native `AnalyzeAudioLevels` is described in [current API](../modules/resolve-21.2.md); a separate full analysis engine is unnecessary for a quick clip measurement. Final-mix QA still needs the actual mix.

## Verification

```text
python -m unittest discover -s tests -v
```

These seven offline tests cover meaningful comparison behavior, unknown evidence, changed gain/fades, actual cut offsets and overwrite protection. They are not a substitute for the [recorded Resolve integration trials](../evidence/resolve-21.2.0.5.md).
