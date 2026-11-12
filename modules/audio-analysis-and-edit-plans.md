# Audio analysis and edit-plan data — reference

> **21.2 compatibility:** this module preserves earlier recipes and evidence. For current signatures, newly tested operations and restrictions, read [Resolve 21.2](resolve-21.2.md). Older `GetProperty`/`SetProperty` and `GetSetting`/`SetSetting` examples require the current dictionary forms.


> [Library index](../GUIDE.md) · Related: [Transcript-driven editing](transcript-driven-editing.md), [Timeline](timeline-and-media.md), [Audio/color](audio-and-color.md), [Render QA](render-and-qa.md)

**Evidence:** FFmpeg filter behavior: upstream-documented. Read-only [`tools/silence_probe.py`](../tools/silence_probe.py): locally tested with synthetic audio. Integration with Resolve `Ripple Delete Silence`, timeline edit APIs and source/timeline time conversion: **not tested** in this package.

## A. Speech-oriented silence detection

`ffmpeg -i INPUT -map 0:a:0 -af "silencedetect=noise=-35dB:d=0.35" -f null -` exposes candidate intervals through messages `silence_start`, `silence_end` and `silence_duration`. `noise` is an amplitude threshold and `duration` is the minimum period before a silence is reported. Output timestamps refer to the input stream's seconds and may be affected by source start times or stream offsets; they are **not** absolute Resolve timeline coordinates.

| Property | Meaning | Limitation |
|---|---|---|
| Threshold (e.g. `-35dB`) | Audio below tolerance can count as silence | Voice recorded quietly, room tone and music affect results |
| Minimum duration (e.g. `0.35`) | Shorter dips do not form a detected interval | Pauses inside rapid speech may be absent |
| `silence_start`, `silence_end` | Boundary candidates in input time | Not guaranteed to be phoneme-safe editing points |
| `mono=1` | Separate channel detection | Mono/stereo/noise differences need care |

**FFmpeg documentation:** https://ffmpeg.org/ffmpeg-filters.html#silencedetect .  
**Reference projects:** https://github.com/samuelgursky/davinci-resolve-mcp and https://github.com/odaiouattara0022-del/davinci-resolve-skill .

The packaged read-only tool supports a diagnostic JSON output and never deletes silence or edits a Resolve timeline:

```text
python tools/silence_probe.py SOURCE.mp4 --noise-db -35 --min-silence 0.35 --output silence.json
```

Example *illustrative* result fragment (not a measurement from the user's video):

```json
{
  "source_file": "SOURCE.mp4",
  "parameters": {"noise_db": -35.0, "min_silence_seconds": 0.35},
  "silences": [
    {"start_seconds": 4.62, "end_seconds": 5.18, "duration_seconds": 0.56}
  ]
}
```

The input may contain continuous background music or essentially no low-level gaps. Zero intervals is a valid analysis result and does not imply an FFmpeg failure. A quiet interval can be a deliberate pause; source-level silence analysis does not establish a meaningful cut by itself.

## B. Transcription + detected silence

Transcription identifies candidate **semantic spans** (ideas, phrase content); silence analysis supplies candidate **acoustic landmarks**. The nearest detected silence is not necessarily a natural edit point. Differences between transcript timestamps and acoustic boundaries are useful review flags, not automatic correction proof.

Distinct levels of evidence:

| Evidence | Describes | Cannot prove |
|---|---|---|
| Word/sentence timestamps | Recognition model alignment | Actual first/last phoneme is complete |
| `silencedetect` | Low signal energy interval | Correct semantics, continuity or sentence boundary |
| RMS/waveform | Audio amplitude shape | Natural dialogue join |
| Frame contact sheet | Adjacent still frame appearance | Motion continuity, speaking cadence |
| Human audition | Perceived speech/room tone continuity | Machine-readable time accuracy on its own |

No generic fixed pre-head/post-tail reserve is safe for every voice recording. Silence may assist cuts only when present and attributable to the dialogue source, not a mixed music track.

## C. Reproducible edit-plan data contract

An **edit-plan** is a machine-readable representation of intended source intervals and expected track relationships, separate from execution. This pattern appears in guarded planning workflows in `samuelgursky/davinci-resolve-mcp`; the schema below is **our own illustrative reference**, not that repository's API or a tested Resolve import format.

```json
{
  "schema_version": "resolve-agent-edit-plan/0.1",
  "source_identity": {"media_path": "SOURCE.mp4", "source_fps": "30000/1001", "duration_frames": 18000},
  "destination": {"timeline_fps": "24/1", "name": "Editorial Draft"},
  "segments": [
    {
      "source_in_frame": 240,
      "source_out_frame_exclusive": 600,
      "source_audio_link": "same_source",
      "reason": "complete statement",
      "boundary_evidence": ["transcript", "silence_candidate"],
      "needs_audio_review": true
    }
  ]
}
```

**Timebase note:** the example's source frames, destination frames, source audio seconds and clip-relative offsets are distinct. `30000/1001` is not 30 fps. Frame endpoints are half-open in this example. The existence and interpretation of Resolve `AppendToTimeline` frame arguments are version/operation-specific and remain documented in the existing [timeline module](timeline-and-media.md).

A project/timeline fingerprint can include stable clip IDs, source path/size, ordered clip ranges, FPS and a hash of a canonical serialization. Such a fingerprint is useful for detecting that the intended source timeline has changed between analysis and montage; it is not a replacement for Resolve's current read-back.

**Verification data** naturally associated with an edit-plan record: source and destination frame ranges, expected duration, media link presence, gap/overlap check, nearest cut frames, signal discontinuity checks, export-path existence and explicit human-review status.

## D. Loudness measures

FFmpeg's `ebur128` filter provides integrated loudness (LUFS), loudness range (LRA), and true peak (dBTP when true-peak mode is enabled). Example reference command:

```text
ffmpeg -hide_banner -i INPUT.mp4 -map 0:a:0 -filter:a "ebur128=peak=true" -f null -
```

This measures audio; it does not apply compression, normalize a Resolve track, set an A2 Ducker or guarantee acceptable speech cadence. Published delivery targets vary by platform and production; no universal target is encoded in this library.

Source: https://ffmpeg.org/ffmpeg-filters.html#ebur128 ; related repository: https://github.com/CiprianSpiridon/davinci-resolve-mcp .

## E. Audit and B-roll catalog data

Offline `.drp`/`.drt` inspections can expose a structured timeline inventory for before/after diffing (clip IDs, track positions, source ranges and media references). The `CiprianSpiridon` repository documents an offline editorial-diff feature; compatibility with our Word Highlight `CompositionBA` is **not assumed**.

A B-roll catalog can describe individual clips or shots with source, in/out, orientation, subject tags, visual description and license/provenance. A JSONL shot-row shape (illustrative):

```json
{"source":"travel_02.mp4","in_seconds":6.1,"out_seconds":10.5,"tags":["bridge","wide shot"],"context":"real footage","essential_source_picture":false}
```

A catalog is a *retrieval aid*, not proof that a shot matches a story or can safely cover the original. Existing [B-roll constraints](transcript-driven-editing.md#4-conceal-a-visible-picture-jump-with-b-roll--only-when-safe) still apply. The `script-to-broll` method is described by https://github.com/AdamGarceau/resolve-toolkit .

## F. Research-only alternatives

- **WhisperX/forced alignment:** possible refining of timestamp candidates. Compatibility with each language, model weight licence, and native Resolve caption reimport remain unresolved locally.
- **Resolve Ripple Delete Silence:** declared and exercised on 21.2.0.5, but failed the signal-preservation test. See [current findings](resolve-21.2.md#rippledeletesilence-documented-not-approved-by-these-tests); retain reviewed source selection for production.
- **Semantic take ranking:** acoustic/fluency measures may prioritize review candidates but do not reliably identify the strongest emotional or visual moment.
- **Native title automation / B-roll indexing:** reference patterns from other projects, not substitutes for installed MCP/tool capabilities.
