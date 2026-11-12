# Resolve 21.2 — current operations and compatibility

> [Start page](../GUIDE.md) · [Tool commands](../tools/README.md) · [Test evidence](../evidence/resolve-21.2.0.5.md)

**Verified environment:** Studio 21.2.0.5, Windows, Python 3.13, 2026-11-05. The installed `.pyi` and changelog are the primary API sources. Tests ran on an imported copy of the open project and a synthetic AV fixture. Production project state was compared before/after. New version numbers do not automatically validate old or new features.

## Current API forms

The current `.pyi` declares dictionary forms. The older singular forms are absent from that file; some may still work at runtime. Use the declared forms in new code rather than depending on compatibility aliases.

| Historical example | Current declared form | Local test scope |
|---|---|---|
| `item.GetProperty('AudioVolume')` | `item.GetProperties().get('AudioVolume')` | Audio clip gain read-back |
| `item.SetProperty('AudioVolume', -3)` | `item.SetProperties({'AudioVolume': -3.0})` | Set/read gain, measured effect and persistence |
| `project.GetSetting('timelineFrameRate')` | `project.GetSettings().get('timelineFrameRate')` | Project settings inventory |
| `project.SetSetting('timelinePlaybackFrameRate', '25')` | `project.SetSettings({'timelinePlaybackFrameRate': '25'})` | Set/read/restore in isolated project |
| `timeline.GetSetting('timelineFrameRate')` | `timeline.GetSettings().get('timelineFrameRate')` | Timeline settings inventory |
| Multiple timeline settings setters | `timeline.SetSettings({'useCustomSettings': '1', 'timelineFrameRate': '30'})` | Empty synthetic test timeline only |

Do not change an occupied production timeline's FPS merely to obtain a preferred number. Project, timeline and export rates have separate roles. Enumerate actual returned keys; a missing property is not a zero or a success. Other dictionary properties need their own task-relevant test.

## Native frame review: use this first for stills

`ExportThumbnails` is new in 21.2. `ExportFrame` predates it; 21.2 adds ROI, maximum dimension and JPEG quality controls.

```python
# timeline is an identified Timeline object. No playhead positioning needed.
result = timeline.ExportThumbnails(
    [{'frameOffset': 0, 'label': 'Opening | f=0'},
     {'frameOffset': 60, 'label': 'Context | f=60'}],
    {'outputType': 'file', 'filePath': absolute_jpg_path,
     'maxDimension': 1600, 'quality': 88})
assert result and result.get('success'), result
# Inspect the produced image; success only establishes export completion.
```

Offsets are **0-based from the target object's start**: timeline-relative for Timeline; item-relative for TimelineItem; source-relative for MediaPoolItem. They are not absolute record frames. For an outgoing/incoming pair use `left.GetEnd() - timeline.GetStartFrame() - 1` and `right.GetStart() - timeline.GetStartFrame()`. Record actual offsets in labels and in JSON. A gap means those two edges are not adjacent.

`maxDimension` caps the **whole grid**, not each cell. Use small batches (the shipped helper defaults to six cells) so faces and text stay legible. Native source and timeline exports were visually inspected. The helper exports all 39 joins in 13 grids and records the target state; inspection remains a separate step.

```python
# Region of interest; normalized fractions of the original width/height.
result = timeline.ExportFrame(0, {
    'outputType': 'file', 'filePath': absolute_png_path,
    'roiX': 0.3, 'roiY': 0.2, 'roiWidth': 0.4, 'roiHeight': 0.6,
    'maxDimension': 640})
assert result and result.get('success'), result
```

The tested ROI returned 640×540 from a 1920×1080 timeline. ROI is useful for text, faces and boundaries; inspect the whole composition too. The tests left the active timeline and playhead unchanged. For earlier builds without this API, use supported `ExportFrame` or `Project.ExportCurrentFrameAsStill` with explicit playhead restoration, or FFmpeg source frames. Never describe that fallback as motion/listening review.

## Native audio level analysis

```python
modes = timeline.GetNormalizeAudioModes()
assert 'EBU R128' in modes
levels = audio_item.AnalyzeAudioLevels('EBU R128')
assert levels is not None
print(levels)  # Integrated: LUFS; TruePeak: dBFS per local API declaration
```

Choose a supported loudness mode; the documentation excludes peak-only `Sample Peak Program` and `True Peak` as arguments. `-100.0` means no level measured, not a usable loudness reading. A local gain change from −3 to −9 dB moved measured integrated loudness and true peak by −6 dB. This establishes sensitivity to that clip gain. It does **not** establish coverage of the final bus, all effects, transitions or the complete mix. Use an actual timeline mix export for final mix measurements and listen separately.

This method was already documented in the 21.1.2 changelog; it is newly verified for this library, not necessarily a 21.2 feature.

## Reversible automatic color

`ApplyAutoColor()`, `GetAutoColorEnabled()`, `SetAutoColorEnabled(bool)` and `ClearAutoColor()` are newly documented for 21.2. On a protected test clip, apply → inspect → disable → compare → re-enable → save/reopen worked; clearing returned its state to `None`. The enabled correction changed the image and persisted. Disabled output matched the initial exported JPEG in our sample.

The local declaration says analysis uses the current playhead frame when that clip is current, otherwise its first frame. Record the frame/context; a different analysis frame can change the result. Use this as a candidate correction, compare skin tones and neighboring shots, and keep only a useful change. Do not grade every clip automatically. Existing shared/remote grades need protection before experimentation.

`GetCDL(nodeIndex)` and `Graph.GetNodeEnabled(nodeIndex)` also returned data in the trial. CDL values remained neutral while auto color visibly changed the picture: a CDL dump is not a full description of all active grading. Real frame comparison remains necessary. Full Color graph round-trip and PhotoAlbum operations were not tested here.

## AV operations and persistence

The original-pair recipe in [AV pairing](av-sync-and-trim.md) was now exercised in the isolated project. Requested source `[60,360)` gave 300 timeline frames for the tested 29.97 source and 299 for the tested 30 source. Linked left/right trims of 3/5 frames reduced both members by 8; explicit pair moves preserved their source relationship. Native gain, audio fade and a four-frame audio transition survived reopen in this sample.

**Video fades still fail persistence in this test.** `SetFades({'FadeIn': 0, 'FadeOut': 8})` immediately returned/read 8 but read 0 after reopen. This was independently reproduced on 21.2.0.5. The native ending `Cross Dissolve` from the existing project remained present across reopening and its final frame was darkened. Prefer that known alternative for this case; inspect it rather than assuming a fade is working.

The snapshot comparison reports real changed fields. Media Pool `Usage` counts are reported separately because they refresh with timeline context. Other differences, such as lazy media resolution metadata, remain visible and need interpretation; a difference is not automatically an editing defect.

## RippleDeleteSilence: documented, not approved by these tests

The local `.pyi` declares `TimelineItem.RippleDeleteSilence(options)` on audio clips, with `threshold`, `preHead`, `postTail`, `minimumToStrip` and `crossFadeAudio`. Its presence was already noted in the 21.1.2 changelog, so the inherited claim “no API established” is obsolete as a documentation claim.

**The current behavior did not pass our correctness check.** A five-second synthetic AV source contained known tones at 1–2 s and 3–4 s. FFmpeg confirmed the two signal intervals and approximately −14 dBFS peak. The first 29.97-fps trial returned `True` and removed the entire linked pair. Two fresh 30-fps trials first measured the audio successfully, then used thresholds −40 and −60 dB, two-frame head/tail padding and a ten-frame minimum: both retained only one 42-frame pair with reported source bounds 108–149, losing wanted signal. Both video and linked audio were affected.

The cause is undetermined. This is a bounded reproducible failure, not proof that every input fails. Keep the operation experimental, do not run it on production footage, and do not treat `True` as validation. The safe workflow remains measured candidate intervals → meaningful source selection → paired edits → playback review.

## Other declared opportunities

The updated Fusion references are `Developer/Fusion/FusionTools.md` and `FusionToolReference.md`. Search the installed files for the exact tool before guessing input names. Extras package management, PhotoAlbum thumbnail/color operations and new project FPS coupling are documented opportunities; no packages were installed and these workflows were not all exercised.

`GetEffectsList('audio')` returned 29 clip effects in the local test, but no Ducker entry. That enumeration describes **clip effects**, not every Track FX capability; native track ducking remains unresolved. Do not infer an unsupported setter or substitute another effect silently.
