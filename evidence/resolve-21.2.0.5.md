# Local validation — Resolve Studio 21.2.0.5

> [Start page](../GUIDE.md) · [Current recipes](../modules/resolve-21.2.md) · [Machine-readable results](local-tests.json)

Tests: **2026-11-05**. Package finalized: **2026-11-06**. Windows, Python 3.13. API source: installed `Developer/Scripting/DaVinciResolveScript.pyi` and `CHANGELOG.md`, with hashes in the JSON. The local changelog is dated 4 Nov 2026. Installed documentation and observed behavior take precedence over older library claims. Public support search did not supply the detailed local signatures; no third-party API claims were needed for these results.

## Isolation and scope

The open project was inventoried, saved and exported to a DRP backup, then imported under a separate validation-project name. Mutating tests ran only in that project, on new AV and synthetic-test timelines. The production project was reopened afterward with its original active timeline and playhead restored. Two before/after captures compared equal across their declared scope. This covers native clip state, properties, settings, markers and media inventory; it is not a byte-for-byte project database or complete Fusion/Color graph proof.

The separate project `Resolve Agent 1.7 - API Validation 20261105` was retained for inspection. Detailed run scripts, backups, before/after snapshots and images remain in the author's workspace `v17_validation` directory. They are deliberately outside this portable library. The bundled JSON contains measurements and documentation hashes without requiring those project files to use the guide.

## What passed, failed or remains unverified

| Test | Observed result | Allowed conclusion |
|---|---|---|
| Timeline native thumbnail grid | Four labelled offsets exported, 1600×916; actual images inspected; playhead unchanged | Working still-frame review path |
| Source native grid / new helper | Three source offsets exported; image inspected | Source mode works on the tested MP4 |
| All primary-track cut frames / new helper | 78 edge frames, 13 grids; captured state/playhead unchanged | Batch export works; export is not proof all images were inspected |
| ROI export | 640×540 for normalized region 0.3, 0.2, 0.4, 0.6 | Working region export and size cap |
| Mixed-FPS source insertion | Requested `[60,360)`: 300 timeline frames for 29.97 source, 299 for 30 source | Use actual returned ranges; not a universal rounding formula |
| Linked trim/move | Left 3 + right 5 shortened both members from 300 to 292; moved together; source mapping retained | Bounded original-pair recipe works |
| Audio gain analysis | −3 dB gain: −32.2269 LUFS / −7.1853 dBFS true peak; −9 dB gain: −38.2269 / −13.1853 | This native clip measurement includes the tested gain |
| Audio gain/fades/transition after reopen | Captured timeline values unchanged | Sample persistence passes for those fields |
| Video fade after reopen | Immediate FadeOut 8; after reopen 0 | Failure reproduced on this build; prefer checked alternative |
| Existing native ending dissolve | Persisted production transition and dark closing frame remained | Useful alternative for the tested ending |
| Auto color | Apply/disable/re-enable worked; enabled correction persisted; clear returned `None` | Reversible candidate grade works on the sample |
| Auto color output | On-image changed; disabled JPEG bytes equal original JPEG | Bypass restored the sampled image; no universal grade recommendation |
| CDL/node status | Neutral CDL and enabled first node returned despite visible auto-color change | These getters do not fully describe the composite grade |
| Playback FPS setting | Changed 29.97 → 25 and restored in test copy | Setting is functional there; no occupied-timeline FPS migration tested |
| RippleDeleteSilence | First trial removed whole pair; two measured 30-fps retrials retained only source frames 108–149 | Correctness failed; production batch use not recommended |
| Audio clip effect discovery | 29 entries, no Ducker | Clip-effect list inspected; track ducking still unresolved |
| Offline helper tests | Seven passed | Comparison semantics, missing evidence, changed gain/fades, edge offsets, output overwrite guard |

The silence fixture had 5 seconds of 30-fps picture and 48 kHz mono PCM audio: a 440 Hz tone of amplitude 0.2 at 1–2 s and 3–4 s, silence elsewhere. FFmpeg independently detected the three silent intervals and about −14 dBFS peak. Rechecks first measured valid audio in Resolve, then applied thresholds −40/−60 dB, two-frame pre/post padding and ten-frame minimum removal, without audio crossfades. Both linked members were altered. Root cause is unknown; neither API presence nor a `True` return establishes correct editing.

## Evidence categories

- **Locally reproduced:** exact operation and read-back exercised in this build; see coverage above.
- **Visually inspected:** named still outputs actually viewed. Not equivalent to playback.
- **Reported earlier:** retained 21.1.2 observations, including specialist title/Fusion work; not silently promoted to 21.2 validation.
- **Documented only:** declared in installed references but not executed here.
- **Failed / experimental:** behavior did not meet the test expectation, or the cause remains unknown.

There was no full film playback or real audio audition in these package-validation trials. Word Highlight DRT import, subtitle generation, PhotoAlbum operations, Extras installation, full grade graph manipulation and Track FX Ducker were not validated. Those limits are explicit so an agent can choose the next useful test instead of repeating unrelated research.
