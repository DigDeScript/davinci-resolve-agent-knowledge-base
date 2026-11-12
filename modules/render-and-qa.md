# Rendering, export and quality verification

> **21.2 compatibility:** this module preserves earlier recipes and evidence. For current signatures, newly tested operations and restrictions, read [Resolve 21.2](resolve-21.2.md). Older `GetProperty`/`SetProperty` and `GetSetting`/`SetSetting` examples require the current dictionary forms.


> [Back to GUIDE.md](../GUIDE.md) | Evidence keys and general safety: [setup-and-safety.md](setup-and-safety.md)

Start with the [GUIDE completion checklist](../workflows/quality-check.md#completion-checklist). Bind QA to the actual timeline revision and record separate coverage for measurements, still frames, motion and listening. For linked sound/picture and before/after persistence checks, see [AV pairing](av-sync-and-trim.md).

## 1.8. Rendering and real quality assurance

```python
# [T/R] Verify available presets and version-specific parameters first.
print(project.GetRenderPresetList())
assert project.LoadRenderPreset('H.264 Master')
assert project.SetCurrentRenderMode(1)  # 1 = single clip; 0 = individual clips
project.SetCurrentRenderFormatAndCodec('mp4', 'H264')
project.SetRenderSettings({
    'TargetDir': out_dir,
    'CustomName': 'final_edit',
    'SelectAllFrames': True,
    'ExportVideo': True, 'ExportAudio': True,
    'FormatWidth': 1920, 'FormatHeight': 1080,
    'FrameRate': 30,
    # For native subtitle burn-in when required and supported in this Resolve build:
    # 'ExportSubtitle': True, 'SubtitleFormat': 'BurnIn',
})
job = project.AddRenderJob()
assert job
project.StartRendering([job])
```

A completed render job does **not** prove the output includes the expected video or audible audio. Use `ffprobe` to check actual streams, codecs, dimensions, FPS, duration, frame count and channels. Inspect frames and play back important cuts and transitions. After audio-only rendering, **reload the desired video preset** before creating the next job: a reported `Complete` MP4 contained no video until the preset was reset [T]. Do not assume `VideoQuality` values are accepted merely because the option appears in documentation.

### Caption burn-in and cut-boundary checks [R]

When the deliverable requires visible native subtitles in the exported picture (not just editable project subtitles), the tested agent reported success using render settings `ExportSubtitle=True` and `SubtitleFormat='BurnIn'` in the installed Resolve build. Confirm acceptance in the active API schema and **inspect the rendered video**, not only render settings or job status. Keep native subtitle clips intact in the editable project.

For transcript-driven or short-form edits, inspect **every** picture cut at the last frames of segment A and first frames of segment B; look for single-frame unrelated inserts. A contact sheet (e.g., ±3 frames around each cut) is a detection aid, not a substitute for motion playback. If B-roll masks a cut, confirm it hides only **visually nonessential material**; do not conceal required demonstrations, screen activity, graphics, or product details. Test the first/last frames of the overlay and check speech audio separately. Full audio playback by a human is stronger evidence than waveform discontinuity or peak-level tests; disclose when it was not performed.

### Production verification additions [R]

- **FPS settings are independent:** check project FPS, each `timeline.GetSetting('timelineFrameRate')`, and the **actual rendered stream** via `ffprobe`. In a reported vertical project, setting `timelinePlaybackFrameRate` returned `False` even though timeline and 20 rendered MP4 streams were 30 fps; investigate the failed setting rather than treating `False` as success.
- **Main-track gap test:** sort the intended continuous primary picture track by `GetStart()`, then report every `(left.GetEnd(), right.GetStart())` mismatch, and separately check first/last coverage. This does not detect visual defects or explain legitimate higher-track overlaps.

```python
# [R] Logical adjacency check; 'video',1 must be intended as a continuous base.
items = sorted(timeline.GetItemListInTrack('video', 1) or [],
               key=lambda clip: clip.GetStart())
gaps_or_overlaps = [(a.GetEnd(), b.GetStart())
                    for a, b in zip(items, items[1:])
                    if a.GetEnd() != b.GetStart()]
```

- **Video file QA:** `ffprobe` streams/duration/dimensions/FPS → full-decode each video to `null` → `ffmpeg blackdetect` with task-appropriate thresholds → sample contact-sheet frames → review the actual motion and audio. In one tested batch, 20 MP4 streams fully decoded; `blackdetect=d=0.05:pix_th=0.06` found no black segments. This is not proof that the edits, framing, subtitles, or sounds are creatively correct.
- **Agent image previews can be fragile in the tested Codex setup:** two Shading investigations ended with `{"detail":"Bad Request"}` after image previews/large operations. During focused API experiments, keep read-back/report outputs small and assign screenshot **evaluation** to the user. **Do not generalize this to a ban on production visual QA**; production work still requires genuine visual review by some reliable means.
- **9:16 scaling:** phone clips can report landscape encoded dimensions yet display portrait in Resolve via rotation metadata. Inspect actual frame output **before** setting `ZoomX/ZoomY` (a reported forced `3.16` crop was incorrect; `1.0` was appropriate for those clips). Keep framing and meaningful visual content visible across the shot.
- **Still-frame QA without a full video render [R]:** The installed Resolve API exposes `Project.ExportCurrentFrameAsStill()`. Position the playhead on a representative frame using supported timeline controls, then use the **actual installed `.pyi` signature** to export/inspect that still. Repeat for opening, transitions, vertical/rotated clips and closing; do not guess required arguments or claim the method is equivalent to reviewing moving video/audio. The reported reel agent used still exports to detect and correct crop.
- **Creative QA differs by footage type:** For an interview, verify coherence of selected statements. For personal/travel/event reels, verify **the actual best moments**, expressive gestures/faces, scene flow, authenticity and whether alternate source intervals would tell a stronger story. A gap-free timeline and technically valid still frames do not prove editorial quality. Flag uncertain choices for human review.

**Color/Fusion bypass [T]:** A graph may exist but its effect or alpha may be bypassed. In one test, a controlled `Shift+D` in the **Edit** context changed the bypass state and fixed output; it is a *toggle*, not a command to press blindly. Validate viewer/export evidence, not only successful graph construction or `SaveProject()`.

---

## External reference: independent audio and change audit (v1.6)

Analysis-side measurements include FFmpeg `ebur128` integrated LUFS, LRA and true peak; project-side state comparison may use clip IDs, ordered source ranges and track placement from `.drp`/`.drt`. See [Audio analysis and edit-plan data](audio-analysis-and-edit-plans.md). `CiprianSpiridon/davinci-resolve-mcp` documents offline project diffing and loudness checks, which remain externally reported rather than locally verified integrations. Neither stream-level metrics nor before/after XML equality prove artistic quality.
