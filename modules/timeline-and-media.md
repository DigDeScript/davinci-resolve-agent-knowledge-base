# Timeline, media, frame mapping, stills, Dynamic Zoom

> **21.2 compatibility:** this module preserves earlier recipes and evidence. For current signatures, newly tested operations and restrictions, read [Resolve 21.2](resolve-21.2.md). Older `GetProperty`/`SetProperty` and `GetSetting`/`SetSetting` examples require the current dictionary forms.


> [Back to GUIDE.md](../GUIDE.md) | Related editorial guidance: [Transcript-driven editing](transcript-driven-editing.md) | Evidence: [setup-and-safety.md](setup-and-safety.md)

For a complete original picture/sound insertion → trim → move → transition trial and sync diagnosis, see [AV pairing, trim and synchronization](av-sync-and-trim.md). It separates reported edit behavior from independently checked current state.

## 1.2. Media, tracks, markers, clip operations

| Desired result | API call | Evidence / caution |
|---|---|---|
| Import media | `items = pool.ImportMedia([absolute_path])` | [R] list of absolute path strings worked; list of `FilePath` dictionaries returned `None` in one edit — verify each import result |
| Add a video track | `timeline.AddTrack('video')` | [S] used by editing scripts |
| Name a video or audio track | `timeline.SetTrackName('video', i, '02 | Titles')` | [S] also supports `'audio'` in archived scripts |
| Insert at a specified frame/track | `pool.AppendToTimeline([clip_info])` | [T/R] read resulting timeline item |
| Move an existing clip | `item.SetPosition({'trackIndex': i, 'startFrame': absolute_frame})` | [R] |
| Adjust a clip's right handles | `item.SetRightOffset(new_remaining_right_offset)` | [T] worked for still/video; **not** for native title extension |
| Remove a clip without ripple | `timeline.DeleteClips([item], False)` | [R] used to replace a title in a duplicate |
| Temporarily disable a clip | `item.SetClipEnabled(False)` | [S] restore previous state after diagnostics |
| Add an editorial marker | `timeline.AddMarker(frame, 'Cyan', name, note, 1)` | [S] used in scripts; verify frame convention |
| Inspect markers | `timeline.GetMarkers()` | [S] |
| Remove a marker at its frame | `timeline.DeleteMarkerAtFrame(frame)` | [S] used while rebuilding markers in a duplicate |
| Advanced trimming, fades, transitions | `Timeline.MoveItems`; `TimelineItem.SetLeftOffset`, `SetFades`, `AddTransition` | [D/?] present in tested `.pyi`; test parameters individually |
| Find unwanted gaps/overlaps | Compare sorted adjacent clips' `GetStart()` / `GetEnd()` | [R] one-track adjacency tested on 20 timelines; not full black-frame QA |

```python
# [T/R] A MediaPoolItem must already exist; source frames != timeline frames.
clip_info = {
    'mediaPoolItem': pool_item,
    'startFrame': 0,
    'endFrame': 90,
    'recordFrame': timeline.GetStartFrame() + 120,
    'trackIndex': 1,
    'mediaType': 1,  # video only; 2 = audio only
}
items = pool.AppendToTimeline([clip_info])
assert items and len(items) == 1
item = items[0]
print(item.GetStart(), item.GetEnd(), item.GetDuration())
```

**Four time systems matter [T/R]:** source frames, absolute timeline/record frames, timeline-relative offsets, and Fusion-local frames. In tested `AppendToTimeline` calls, source `[0,30)` produced **30 frames**; `endFrame` was effectively exclusive. But `SetMarkInOut(in, out, 'video')` used for title insertion had an **inclusive** `out`. `SetPosition.startFrame` and `recordFrame` used absolute timeline frames; In/Out marks were relative to timeline start. A 25 fps source inside a 30 fps timeline gave an observed mapping of timeline 90 frames to Fusion-local 75 frames. Do not derive source frame from `GetLeftOffset()` using an unverified simple ratio. Inspect `comp.GetAttrs()` including `COMPN_RenderStart/End` and compare at least two real frames before generating time-dependent automation.

### Native still image with a longer duration

```python
# [T] Native still may initially appear as a 24-frame timeline item.
item = pool.AppendToTimeline([{
    'mediaPoolItem': still_item,
    'startFrame': 0, 'endFrame': 420,
    'recordFrame': timeline.GetStartFrame(),
    'trackIndex': 1, 'mediaType': 1,
}])[0]
requested = 420
remaining_handles = item.GetRightOffset()  # NOT the item duration
if item.GetDuration() != requested:
    assert item.SetRightOffset(remaining_handles - (requested - item.GetDuration()))
assert item.GetDuration() == requested
```

This is **verified for a native still**, not as a universal generator-resize method. Native title / Fusion Composition extension through negative `SetRightOffset` failed in the reported tests. Do not transcode the still into a video merely to obtain a longer timeline clip.

### Native photo Dynamic Zoom: small API recipe [R]

```python
# Inspect real properties on the chosen photo timeline item.
props = item.GetProperty()     # On newer builds inspect GetProperties() too.
assert 'DynamicZoomEnabled' in props
assert item.SetProperty('DynamicZoomEnabled', True)
assert bool(item.GetProperty('DynamicZoomEnabled')) is True
# Optional: inspect and verify item.SetProperty('DynamicZoomEase', 3)
# in builds where 3 = Ease In and Out.
```

`DynamicZoomEase` values observed in the user/agent tests: `0` Linear, `1` Ease In, `2` Ease Out, `3` Ease In and Out. **Ordinary, gentle photo moves: prefer `3`**, while checking actual motion and subject framing. The API did **not** expose a validated start/end framing or Zoom In/Out **Swap** method through tested timeline properties. The Inspector's manual **Swap** changes direction; a narrowly controlled UI action is an alternative when available. **Do not simulate Swap with `SetSpeed({'Percentage': -100.0})`:** in the tested still clip, `SetSpeed` returned `False`, speed stayed `0.0` and length stayed 39 frames. Reversing a video would also reverse its content, which is undesirable when only changing zoom direction.

**Markers and track names are editorial aids:** add markers for meaningful events, not every generated intermediate. Preserve existing markers when editing a user's timeline; the script that deleted them did so in a new versioned timeline.

## Phone orientation, rotation metadata and scaling [R]

Do **not** derive 9:16 scaling just from encoded width/height: a phone file may store landscape pixel dimensions plus rotation metadata, which Resolve has already applied. In the reported 1080×1920 edit, forcing `ZoomX/ZoomY = 3.16` overcropped a correctly oriented phone clip; reset to `1.0` worked for those clips. Inspect a still frame or reliable viewer at **multiple moments** before computing any extra zoom. Judge framing of faces, important objects and horizon after Resolve has interpreted orientation; never assert a universal zoom factor for rotated sources. See [Render and QA](render-and-qa.md) for a non-video-export frame-check method.

For media import, first try a list of one or more **absolute file-path strings**, checking that returned MediaPool items are valid. A batch of `FilePath` dictionaries returned `None` in one observed Resolve session while one-by-one imports worked. Do not infer that all object/dictionary overloads are universally unsupported; inspect the installed `.pyi` and use the verified form for the current environment.

## B-roll overlays around editorial cuts

For jump cuts in podcasts/interviews, an overlay on a higher video track can conceal the visible picture change while keeping original speech on its native audio track. **Only use B-roll when the underlying picture being obscured is not important to understand the video.** Never cover a necessary demo, screen control action, chart, product detail, reference text or other essential visual. Source candidates from relevant footage/photos in the project first; generating supplementary visuals is optional only if an appropriate generation tool exists. Review overlay entry/exit and the underlying edit. See [Transcript-driven editing](transcript-driven-editing.md).

## External reference: typed editing plans and state comparison (v1.6)

A JSON source-segment plan with rational FPS strings, source-in/source-out-exclusive frames, explicit media identity and link relationships separates source selection from timeline execution. A small illustrative data contract is in [Audio analysis and edit-plan data](audio-analysis-and-edit-plans.md). Its schema is our example, not an official Resolve import schema. Inspecting source/timeline identities before and after mutation offers a reproducibility check; it does not establish support for direct ripple deletion or speed/pitch APIs.
