# Known pitfalls and safer alternatives

> **21.2 compatibility:** this module preserves earlier recipes and evidence. For current signatures, newly tested operations and restrictions, read [Resolve 21.2](resolve-21.2.md). Older `GetProperty`/`SetProperty` and `GetSetting`/`SetSetting` examples require the current dictionary forms.


> [Back to GUIDE.md](../GUIDE.md) | Evidence keys and general safety: [setup-and-safety.md](setup-and-safety.md)

# 3. Known traps — if you do X → you risk Y → use Z

| Trap or wrong assumption | Undesirable result | Preferred approach |
|---|---|---|
| Render captions as transparent PNG/MOV | Text cannot be edited in Inspector | Native Text+ timeline clip; verify actual Inspector controls |
| Put Border Fill in Shading element 1 while it is named `White Solid Fill` | Inspector labels lie: switching off "White Solid Fill" removes the background, not the text | Reserve element 1 for glyph `Text Fill`, element 2 for correctly named decoration |
| Keep a `Red Outline` name after converting that slot to Border Fill | Human edits the wrong layer; reusable template becomes misleading | Set `NameN` whenever changing `ElementShapeN` |
| Rely on Shading slot number or default priority as layer order | Background can completely hide text | Set `SortShadingElements=0`, `PriorityBack1=7`, `PriorityBack2=4`, verify actual glyph/background roles |
| Copy the one-based `GetInputList()` enum-label key as an input value | Wrong Shading or Blending mode | Verify actual values via `SetInput`/`GetInput`; tested `Overlap2=2` is Composite, while label metadata keyed it by `3` |
| Use tiny Title Size for a 9:16 layout | Hard-to-read captions, inconsistent editing baseline | Preserve native Size; recommend around `0.1`, shorten/reflow text rather than blindly shrinking |
| Treat `SetInput()` return of `None` as failure or success | False success/failure reports | Read back `GetInput()` and verify output at the appropriate stage |
| Use Word/Character semi-transparent backgrounds without considering overlap | Unexpected dark strips behind words/letters | Prefer `Border Fill → Line`, `Opacity2=0.70`, Composite; use per-word/glyph backgrounds only by design |
| Turn on a template's default Black Shadow for every title | Often produces a low/right offset shadow of little readability value | Use no drop shadow by default; only tune on explicit request; slot IDs are template-dependent |
| Supply absolute timeline frames to `SetMarkInOut` | Marks appear outside intended time range and can disrupt playback | Use offsets relative to `timeline.GetStartFrame()`, inclusive OUT, and clear/restore marks in `finally` |
| Try to reverse a still to invert Dynamic Zoom | `SetSpeed(-100%)` returned False for tested still, no direction change | Use Inspector Swap, or separately controllable Fusion Transform animation |
| Let the editing agent stop halfway through a real production deliverable for visual confirmation | Incomplete project is handed off | Agent completes autonomous native assembly and QA; user-only visual inspections are **for interactive experiments**, not a substitute for production delivery |
| Animate only with `SetExpression(time...)` | No ordinary editable Spline keyframes | `BezierSpline` + `SetInput(..., frame)` where supported |
| Overwrite an already animated input | User's keyframes/modifier may be lost | Inspect connections and existing keys; reject unsafe writes |
| Treat a Fusion Composition as an equally convenient title | Editing text may require navigating Fusion | Use native `InsertFusionTitleIntoTimeline('Text+')` for simple captions |
| Insert native title/composition without video In/Out marks | Default short length (e.g. 24 frames) | Set marks with inclusive Out before insertion |
| Extend only `COMPN_GlobalEnd/RenderEnd` | Edit timeline item remains short | Create/verify native item at required timeline duration |
| Apply still's `SetRightOffset` trick to title | Tested title extension returned `False` | Recreate title using validated In/Out, replace non-ripple |
| Render a still to video to lengthen it | Unnecessary intermediate and harder edits | Keep native still; validated right-handle adjustment |
| Use `start+duration-1` as source `endFrame` for AppendToTimeline | One-frame gaps in tested case | Check actual half-open insertion semantics and duration |
| Assume timeline/source/Fusion times are identical | Masks, tracking and animation drift | Inspect FPS, global/relative/local ranges and test frames |
| Guess TextPlus `WriteOnEnd` input | Input missing in tested build | Inspect inputs; actual IDs were `Start` and `End` |
| Create `comp.AddTool('CustomTool')` | Returned `None` in tested build | Use the registered ID `Custom` |
| Create every Fusion node at `(0,0)` | Unreadable overlapping graph | Specify `AddTool(type,x,y)` or `FlowView.SetPos` |
| Assume `CurrentFrame` is always available | Cannot access FlowView in some comp contexts | Activate comp or use validated export/import layout fallback |
| Treat `CopySettings()` as whole graph backup | Could contain only selected nodes | `ExportFusionComp` or a verified complete graph inventory |
| Trust `AddFusionComp`/`SaveProject()==True` alone | Effect may vanish or render incorrectly after reopen | Reopen and check real rendered frames, nodes and connections |
| Disconnect a graph for diagnosis then reuse stale output handles | Black image or missing connection after reopen | Debug a duplicate; save a known-good `.comp` |
| Ignore Color/Fusion bypass | Alpha/effects missing despite existing graph | Verify bypass state and representative output, avoid blind toggle |
| Misorder layers or omit an occlusion matte | Objects appear in front when they belong behind | Plan foreground/background/mattes by depth and time |
| Treat DepthMap as a guaranteed semantic person selection | Ground/trees may also be selected | Compare DepthMap with Magic Mask, roto or replaceable person matte |
| Treat `MagicMask.Strokes` as a Tool | API TypeError | It is specialized data; stroke/track automation is unresolved |
| Treat grayscale matte PNG as alpha automatically | Invalid transparency/composite | Map matte channel to RGB/alpha via tested `Custom` operation |
| Judge a generated matte using only a few still frames | Edge flicker or drifting cutout can be missed | Inspect full movement, hair/hands/feet, light/dark backgrounds |
| Leave a clean plate active after it is no longer needed | Frozen/black or incorrect background | Restrict its time interval and restore original moving source |
| Assume GPU/Motion Blur is the only source of warping | Edge artifact may persist | Compare renders; in one tested CornerPositioner case `UseGPU=0` helped |
| Bake voice and music into the only active WAV | Separate adjustments become difficult | Distinct original/editable audio tracks |
| Raise voice gain before checking noise | Amplifies rumble/hiss | Listen, inspect noise, filter appropriately, then gain |
| Bake color into replacement footage | Grade is difficult to tweak | Native Color or Fusion correction with source preserved |
| Set `SetCurrentRenderMode(0)` expecting one video | Outputs individual clips | `1` was single-clip mode in tested build |
| Rely on render job `Complete` | Video or audible audio may be absent | `ffprobe` + playback/visual inspection |
| Infer the current cut from old JSON or timeline name | Human changes overwritten or an old version restored | Fresh inventory and targeted edits in a duplicate |
| Trust UI `set_value` without commit | API still shows the old keyframe | Commit field (e.g. Tab), then `GetInput`/`GetKeyFrames` |
| Execute another script by splitting its source text | Hidden dependencies and brittle reuse | Explicit imports/functions and a maintained entry point |

## Native Word Highlight / DRT lessons [R]

| Trap | Why it fails | Required behavior |
|---|---|---|
| Modify `CompositionBA` without updating the embedded length at uncompressed outer offset 142 | Resolve imported only the old declared byte count, truncating the inner zlib stream and rendering black | Rewrite all three length headers and verify round-trip integrity |
| Assume DRT import success means effect works | Seven subtitle clips survived even when Fusion failed | Re-export, verify both zlib streams and inspect actual playback |
| Assume all RGB inputs exist explicitly | Default `Red1` was omitted; highlight channels could also be implicit | Inspect actual macro; do not guess missing input insertion |
| Confuse Text+ titles with Word Highlight | Word Highlight is attached to the **subtitle track**, not individual text clips | Use [word-highlight.md](word-highlight.md) |
| Treat `UpdateWordAnimation` console warning on color selection as proof of bad DRT | Same warning appeared on a never-imported native timeline; playback worked | Record warning separately and validate actual animation |

## Recent editorial findings [R, 2026-11-02]

| Trap | Why it fails | Required behavior |
|---|---|---|
| Add the same 2–3 frame handle to every spoken sentence | Can introduce the next word or one-frame unrelated picture | Use verified boundaries; check at every cut |
| Treat successful transcription as exact phoneme boundaries | Automatic word time marks may be approximate | Inspect/listen around selected first and last words |
| Cover every cut with B-roll regardless of importance | May hide the demonstration, chart or on-screen evidence necessary for meaning | Use B-roll **only if hidden video is nonessential** |
| Assume silence removal handles all recordings | Continuous sound/music/background noise confuses silence detection | Apply only with actual pauses; tune settings and review |
| Assume `install` can recolor an already occupied subtitle track | It intentionally rejects existing effect holders | Use a clean duplicate with captions preserved; do not regenerate edited captions by default |
| Assume native subtitles automatically appear in rendered MP4 | Caption burn-in requires render configuration and actual file QA | Verify `ExportSubtitle` / `SubtitleFormat` on installed build and inspect output |
| Use `Auto` transcription without checking the source language | In one edit it generated unrelated English text for non-English speech | Identify actual language first; inspect Extended Language Support, choose supported language explicitly and reject nonsensical transcripts |
| Crop phone video based only on encoded width/height | Rotation metadata may already be applied by Resolve; forced `ZoomX/ZoomY=3.16` cropped too far | Check Resolve-exported frames and actual displayed orientation before modifying zoom |
| Pass only `FilePath` dictionaries to `ImportMedia` without validating result | That input form returned `None` in one observed session | Try absolute path strings and inspect returned MediaPool items; check installed signatures |
| Treat a personal/event reel like a keyword-selected podcast | Technically sound segments may omit the strongest moment and spoil authentic scene flow | Select expressive, meaningful visuals first, produce reviewable draft and identify choices needing human judgement |
| Assume automated QA ensures natural audio or integrated Ducker is available | Cut-boundary phonemes may still be wrong; native A2 Ducker could not be controlled through tested API/UI | Listen at joins; report manual review needed and Ducker as an unresolved step, not a completed effect |
