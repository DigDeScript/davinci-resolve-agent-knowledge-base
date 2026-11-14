# Text reveal promo: bounded Fusion observations

**Status:** locally tested by the proposing editing agent; not independently validated.
**Date:** 2026-11-14. **Environment:** DaVinci Resolve Studio 21.2.0.6, Windows, Python 3.13.5, installed Resolve/Fusion Python bridge. Synthetic 1080 × 1920, 30 fps composition, item-relative frame 45. No client media or project files are included.

## Unavailable font style can make a downstream composite black

Starting graph: opaque colored Background and TextPlus feed a Merge, then MediaOut. Text is `FONT CHECK`, size 0.1, centered. The installed Consolas styles are Bold, Bold Italic, Italic and Regular.

1. Set TextPlus `Font='Consolas'`, `Style='Medium'` (absent from that family).
2. Read `GetInput('Style')`: it returns `Medium`, which does not establish font availability.
3. Export item-relative frame 45 with `ExportFrame` to PNG: `success=True`, but RGB extrema are `(0,0)` on every channel. The colored background is also absent.
4. Change only Style to `Regular`, keeping the graph connected.
5. Export the same frame: `success=True`; RGB extrema become `(25,234)`, `(8,242)`, `(5,244)` and the text/background are present.

This reproduces the symptom and recovery on one build/font/graph. It does not prove all missing fonts/styles fail identically. No font installation, Resolve restart, bypass toggle or cache deletion was needed for this trial. Persistence of this diagnostic failure after project reopen was not tested.

**Prevention:** query `fusion.FontManager.GetFontList()` and validate the family/style pair before generating multiple scenes. **Diagnosis:** on a disposable copy, compare a known opaque source, isolated text and successive Merge outputs; change one condition at a time. Do not interpret an export-success flag as visible-content validation.

## Published group output is not necessarily `.Output`

On the same build, a custom GroupOperator with a published main image output returned `None` for Python `group.Output`, while `group.FindMainOutput(1)` returned an output handle. Connecting that handle to a Merge worked in the promo's rendered frame checks. Read-back named the internal result tool; this alone was not a broken group connection.

Use the main-output lookup for a group known to publish its image on slot 1, verify that it exists, and inspect the connected input and image. Do not assume every group has an image output or that slot 1 is appropriate for every tool. This observation is scoped to the tested custom group, not a universal group serialization rule.

## Existing guidance that would have prevented rework

- [Timeline and media](../modules/timeline-and-media.md) already distinguishes tested half-open `AppendToTimeline` ranges from inclusive insertion marks. The first promo attempt requested 89 rather than 90 frames.
- [Render and QA](../modules/render-and-qa.md) already warns that documented `VideoQuality` values may be rejected. In the earlier edit, numeric 20000 and `Best` both returned False with the chosen NVIDIA codec. No universal replacement value is proposed.
- [Audience engagement](../modules/audience-engagement.md) already calls for viewer orientation, demonstrated value and a supplied destination. A polished generic headline plus a vague discovery CTA did not sufficiently explain the host application or acquisition steps.
- [Editing standards](../modules/editing-standards.md) already favors native items, readable graphs, independent audio and saved-state verification. The earlier edit used neutral MP4 canvases and a combined soundtrack, although native compositions and separate stems were feasible.

## Validation boundary

The font experiment includes API read-back and exported-frame pixel measurements; its restored image was inspected. The original promo had complete file decoding, frame sampling and audio-level measurements. Those are not proof of full motion playback, pleasant sound, or conversion performance. These claims require separate coverage. No viewer-conversion experiment was conducted.

## Offline validator portability

The library's original syntax check wrote bytecode under `Path('/tmp')`. On this restricted Windows workspace that resolved to an unwritable drive-root directory and produced `WinError 5`, misleadingly reported as Python syntax errors. The proposed change uses `compile(source_bytes, filename, "exec")` without executing the code, so syntax validation requires no temporary directory or bytecode file. An initial TemporaryDirectory approach also encountered sandbox-specific Windows permissions; removing unnecessary writes avoids both path assumptions. This changes offline validation only; it does not certify Resolve behavior.
