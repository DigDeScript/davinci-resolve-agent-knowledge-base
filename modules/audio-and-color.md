# Audio, transcription, color and stabilization

> **21.2 compatibility:** this module preserves earlier recipes and evidence. For current signatures, newly tested operations and restrictions, read [Resolve 21.2](resolve-21.2.md). Older `GetProperty`/`SetProperty` and `GetSetting`/`SetSetting` examples require the current dictionary forms.


> [Back to GUIDE.md](../GUIDE.md) | Evidence keys and general safety: [setup-and-safety.md](setup-and-safety.md)

## 1.7. Audio, transcription, color, stabilization

| Desired result | Available method / direction | Evidence |
|---|---|---|
| Place independent music, voice, SFX | `pool.AppendToTimeline([{'mediaPoolItem': audio_item, ..., 'mediaType': 2, 'trackIndex': audio_track}])` | [T/S] verify audio routing |
| Preserve editable sound | Keep distinct voice/music/SFX tracks; export mix only for delivery | [T] workflow |
| Native gain, EQ, fades, pan, Fairlight FX | Inspect installed `.pyi` and test isolated operation | [?] no complete verified API library |
| Multilingual speech-to-text | Determine actual source language first; where needed use a supported transcription engine with explicit language code (`language=<ISO code>`), FFmpeg→PCM if required | [R/T] transcripts and word timings require verification |
| Stabilize clip | `item.Stabilize()` | [T] used on 23 clips; inspect crop/artifacts |
| Apply editable Fusion-based color | Native Fusion `ColorCorrector` tool | [T] not the same as Color page grade |
| Apply Color page grades | `Timeline.CopyGrades`, `TimelineItem.SetCDL`, LUT/DRX pathways | [D/?] verify signatures and human editability |

**Audio:** inspect low-frequency rumble and defects before increasing gain. VAD and transcript timestamps may propose speech cuts, but review by listening; choose boundaries based on actual pauses and intact consonants/breaths, not a fixed frame margin. Avoid replacing the only active voice/music tracks with a single premixed WAV. If processing absolutely requires external audio stems, keep the stems independent and preserve source links.

**Color:** keep source media unchanged; apply corrections as editable Resolve/Fusion operations, not by generating a permanently graded video replacement. If the human must adjust a **Color page** grade, do not present a Fusion ColorCorrector as an equivalent editing experience. Visually verify subtle changes for natural skin tones and overall consistency.

## Speech edit boundaries and optional silence removal [R / UI method]

Resolve has `Ripple Delete Silence` / `Remove Silence` controls for recordings with discernible pauses, including threshold and pre/post reserves. This is useful as an **optional pre-pass** in a protected working copy, not a universal recipe. Update for 21.2: the API is declared, but controlled tests removed wanted signal. Do not batch it on production footage; see [current findings](resolve-21.2.md#rippledeletesilence-documented-not-approved-by-these-tests). If the recording has continuous sound, music, overlaps or noisy ambience, skip this method. In the tested editing task, mechanically extending each sentence by two frames before and three after sometimes pulled unwanted syllables/picture from the next sentence. Use source-verified cut boundaries; listen near each join. See [Transcript-driven editing](transcript-driven-editing.md) and [Render and QA](render-and-qa.md).

**Language preflight before transcription or subtitles [R / user-observed UI]:** Inspect or listen to source speech to establish its language(s) **before** requesting transcription or `CreateSubtitlesFromAudio()`. Do not silently accept `Auto`: one reported Resolve session misidentified source speech as English and generated unrelated text. Explicitly select the correct supported language when possible. In Resolve transcription settings, **Enable Extended Language Support** expands the language list; depending on installation an additional language package may be required. Confirm the option and the language in the *installed* Resolve UI/API rather than assuming every native caption language exists. If the language is unsupported or recognition is obviously unrelated, reject the transcript as an edit plan; use a suitable external speech-to-text method if authorized/available or ask the user to review. Native subtitle generation and external transcripts are separate workflows.

**Transcription state:** `GetTranscription()` may return `None` before transcription exists. Treat it as a state to handle; verify available Resolve method signatures and run `TranscribeAudio()` when supported. The resulting word times still require cut-by-cut QA.

**Native Ducker is not yet automated [R].** In one edit, the agent could not enable the A2 music-track **Track FX → Ducker** with A1 dialogue as source: programmatic Ducker controls were not found in the inspected `.pyi` and GUI control attempts timed out. This is an observed automation blocker, not proof the effect is impossible to automate. Preserve A1/A2 unchanged and report the missing operation; do **not** invent undocumented setters or silently substitute unrelated processing. Future study of UI or exported track settings is separate from editing production footage.

## External reference: loudness and silence diagnostics (v1.6)

FFmpeg `silencedetect` exposes amplitude-threshold-based pause candidates; `ebur128=peak=true` measures integrated loudness (LUFS), loudness range (LRA) and true peak (dBTP). These are analysis tools, not native Resolve Track FX controls. Details, examples and uncertainty boundaries are cataloged in [Audio analysis and edit-plan data](audio-analysis-and-edit-plans.md). They cannot by themselves validate the naturalness of speech edits.
