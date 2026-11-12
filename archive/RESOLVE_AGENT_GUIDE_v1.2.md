# RESOLVE AGENT GUIDE — practical API reference and editing standards

**Updated:** 2026-11-01  
**Version:** v1.2  
**Purpose:** A compact operational reference for an AI agent editing video in **DaVinci Resolve through the Resolve/Fusion API**. Prioritize a correct, intelligible, **human-editable Resolve project**, not merely a finished MP4 or the fastest workaround.

**Evidence environment:** Reports and archived scripts from DaVinci Resolve **Studio 21.1.2.10**, Windows, Python 3.13. This guide consolidates those observations plus the user-reviewed November Text+ Shading rebuild. Commands were **not rerun in this document-editing session**. Check your installed API before relying on behavior in another build.

**Evidence labels:**
- **[R]** Reported working with read-back, render, user visual inspection, or save/reopen evidence from the editing agent; check the specific assertion made.
- **[T]** Reported as tested by an earlier editing agent, without independent reproduction here.
- **[F]** Observed in the earlier Fusion / ExplodingText experiments.
- **[S]** Exact use appears in the archived Python scripts; successful runtime behavior was not separately reverified here.
- **[D]** Appears in documented/local API definitions; the particular workflow still needs testing.
- **[?]** Hypothesis or unverified workflow. **Never present it as a tested solution.**

**Non-negotiable rule:** Prefer native, nondestructive Resolve operations. Keep text, animation, sound, color, and compositing editable. Use rendered intermediate media only for a justified purpose; record what cannot be edited afterward. Validate actual project state and output, not only API return values.

---

# 1. API command reference — desired result → command → verification

## 1.1. Connect, inspect, protect

| Desired result | API call | Evidence / note |
|---|---|---|
| Connect to Resolve | `dvr.scriptapp('Resolve')` | [T/R] |
| Get current project | `resolve.GetProjectManager().GetCurrentProject()` | [T/R] |
| Get active timeline | `project.GetCurrentTimeline()` | [T/R] |
| Enumerate timelines | `project.GetTimelineCount()`, `project.GetTimelineByIndex(i)` | [R] indices start at 1 |
| Duplicate the working timeline | `copy = timeline.DuplicateTimeline('New English Name')` | [R] then `project.SetCurrentTimeline(copy)` |
| Inspect Media Pool bins | `project.GetMediaPool().GetRootFolder()`; `folder.GetSubFolderList()`, `GetClipList()` | [T/D] recurse |
| Read a video/audio track | `timeline.GetTrackCount('video')`, `GetItemListInTrack('video', i)` | [T/R] |
| Read media properties | `media_item.GetClipProperty()` | [R/D] inspect returned keys |
| Read timeline frame rate and origin | `timeline.GetSetting('timelineFrameRate')`, `GetStartFrame()` | [T/D] |
| Inspect a timeline clip | `item.GetStart()`, `GetEnd()`, `GetDuration()`, `GetPosition()` | [R] |
| Read clip offsets and Fusion comps | `item.GetLeftOffset()`, `GetRightOffset()`, `GetFusionCompCount()` | [R] |
| Save live project | `pm.SaveProject()` | [T] verify reload |
| Export a `.drp` project backup | `pm.ExportProject(project.GetName(), absolute_drp_path)` | [R] does not bundle media |
| Open required UI context | `resolve.OpenPage('edit')`, `resolve.OpenPage('fusion')` | [T] |

```python
# [T/R] Windows bridge location in the tested environment; verify locally.
import sys
sys.path.insert(0, r'C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules')
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp('Resolve')
assert resolve is not None
pm = resolve.GetProjectManager()
project = pm.GetCurrentProject()
assert project is not None
timeline = project.GetCurrentTimeline()
assert timeline is not None
pool = project.GetMediaPool()
print(project.GetName(), timeline.GetName(), timeline.GetStartFrame())
```

**Local documentation first:** In the tested installation, use `Developer/Scripting/README.md` and `DaVinciResolveScript.pyi`, plus the installed Fusion scripting references. Do not assume the older `README.txt` filename exists. Enumerate any connected MCP tools and inspect their **actual schemas**. The Resolve Python proxy can expose misleading apparent attributes: verify methods in the local definitions and with a minimal operation, not `hasattr()` alone.

**State protection:** Inspect the *live* timeline, not just its name, old JSON, or an archived manifest. Duplicate before experimentation. Keep one current manifest of the intended changes and protect manual edits. Do not rerun a script that creates another timeline without checking whether it already exists.

## 1.2. Media, tracks, markers, clip operations

| Desired result | API call | Evidence / caution |
|---|---|---|
| Import media | `items = pool.ImportMedia([absolute_path])` | [S] used for separate audio; check result |
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

## 1.3. Native timeline Text+ titles — preferred for ordinary captions

| Desired result | API | Evidence |
|---|---|---|
| Insert a genuine Text+ timeline clip | `timeline.InsertFusionTitleIntoTimeline('Text+')` | [R] |
| Give the title exactly N frames on creation | `SetMarkInOut(offset, offset+N-1, 'video')` **before** insertion | [R] verified at 90 and 254 frames |
| Place on the right track and time | `title.SetPosition({'trackIndex': i, 'startFrame': absolute_frame})` | [R] |
| Obtain title's Fusion graph | `title.GetFusionCompByIndex(1)` | [R] |
| Find TextPlus without guessing its name | `[n for n in comp.GetToolList(False).values() if n.ID == 'TextPlus']` | [R] |
| Set native title inputs | `text.SetInput('StyledText'/'Font'/'Style'/'Size'/'Center', value)` | [R] for tested template; inspect inputs |
| Replace a shorter title | Create/verify new title, then `timeline.DeleteClips([old_title], False)` | [R] done in a duplicate |
| Insert a complex native Fusion Composition | `timeline.InsertFusionCompositionIntoTimeline()` after video In/Out | [T] also supports tested duration control |

```python
# [R] Example: 90-frame native Text+ with exact track/position.
# Precondition: the staging In/Out area and destination track/range are safe.
N = 90
staging_offset = 600  # EXAMPLE ONLY: find an unoccupied range
track = 2
absolute_start = timeline.GetStartFrame() + 120
old_marks = timeline.GetMarkInOut()
old_head = timeline.GetCurrentTimecode()
try:
    assert timeline.SetMarkInOut(staging_offset, staging_offset + N - 1, 'video')
    title = timeline.InsertFusionTitleIntoTimeline('Text+')
    assert title and title.GetDuration() == N
    assert title.GetMediaPoolItem() is None
    assert title.SetPosition({'trackIndex': track, 'startFrame': absolute_start})
    comp = title.GetFusionCompByIndex(1)
    text = next(n for n in comp.GetToolList(False).values() if n.ID == 'TextPlus')
    text.SetInput('StyledText', 'Editable title')
    text.SetInput('Font', 'Segoe UI')
    # Preserve the native Size; recommended portrait-title baseline is 0.1.
    native_size = text.GetInput('Size')
    assert text.GetInput('StyledText') == 'Editable title'
    print('native Size:', native_size)
finally:
    timeline.ClearMarkInOut('video')
    saved = old_marks.get('video', {})
    if 'in' in saved and 'out' in saved:
        timeline.SetMarkInOut(saved['in'], saved['out'], 'video')
    timeline.SetCurrentTimecode(old_head)
```

The built-in Text+ template's TextPlus node was named **`Template`**, not `Text1`, in the tested build. Look up its `ID`, not a guessed name. `GetSelectedClips()` may be empty after API insertion; an existing timeline title is not proof it is selected in Edit Inspector. Native Text+ is preferred to a Fusion Composition containing text because the latter may require the human editor to navigate into Fusion. Both are preferable to baked PNG/MOV titles.

For a **native Fusion Composition**, the same video In/Out technique controlled its duration, followed by `SetPosition(...)`. `COMPN_GlobalEnd` / `COMPN_RenderEnd` changes do **not** lengthen its Edit timeline clip. To change a native generator's duration when resizing is unverified, create and verify a replacement of the desired duration **before** deleting the old item; use non-ripple deletion.

### Text+ Shading: native, editable text + outline/background [R]

**Verified environment and scope:** Resolve Studio 21.1.2.10, a 1080×1920 test timeline, eight native Text+ titles, Fusion API input read-backs, and the user's Inspector/visual checks. The user subsequently repositioned titles for a single comparison screenshot: **their screenshot positions are not the script's original placements**. This test confirms the specified shading configuration and visible examples, **not** a separate save/reopen inspection of every title or programmatic pixel-accurate bounds detection.

**First inspect the live TextPlus input metadata.** The tested `Text+` template exposed these zero-based *values* (its metadata menu labels may be indexed from **1**, so do not copy menu-label keys directly as `SetInput` values):

| Input | Accepted value / meaning in tested build | Notes |
|---|---|---|
| `ElementShapeN` | `0` Text Fill; `1` Text Outline; `2` Border Fill; `3` Border Outline | `N` is the Shading element slot, not drawing order |
| `LevelN` | `0` Text; `1` Line; `2` Word; `3` Character | Used to group border/background geometry |
| `EnabledN` | `1` enabled; `0` disabled | Enabling element 2 exposes additional inputs |
| `NameN` | Descriptive string | Update when changing an element's purpose |
| `SortShadingElements` | `0` = Priority | Explicitly set for priority sorting |
| `PriorityBackN` | Higher value toward the **front** | Tested: main text `7`, background/outline `4` |
| `OpacityN` | `0.70` for *background*; `1.0` for main text | This is visual house style, not an API requirement |
| `OverlapN` | `2` = Composite in tested read-back/Inspector | Metadata label table contained `3: "Composite"`; **enum value and label index differ** |
| `RedN`, `GreenN`, `BlueN`, `AlphaN` | Color/alpha channels | Keep `AlphaN=1.0` and use `OpacityN` for background opacity in this recipe |
| `ThicknessN` | Outline or border thickness | Style-specific; inspect accepted range and rendering |
| `ExtendHorizontalN`, `ExtendVerticalN`, `RoundN` | Background padding / corner settings | Inputs seen in earlier test; systematic visual behavior not fully documented |

**Correct element order is a human-editability requirement, not merely a rendered appearance:**

- **Element 1: `White Solid Fill` = actual main glyphs (`ElementShape1=0`, white, opacity `1.0`, priority `7`).** Keep this first even if an alternative arrangement could render correctly.
- **Element 2: decoration** (outline or border). Change its `Name2` to match its actual purpose, e.g. `Line Background`, `Text Outline`, `Border Outline`; put it **behind** the glyphs with priority `4`. Do not leave `Red Outline` when the slot has been repurposed as a background.
- Disable unused elements 3–8. Standard text-only titles need no second element; shadows are opt-in only.

```python
# [R] Apply this to the TextPlus node of a native Text+ title.
# Read metadata first; never assume slots on an unknown/custom template.
node = next(n for n in title.GetFusionCompByIndex(1).GetToolList(False).values()
            if n.ID == 'TextPlus')
node.SetInput('SortShadingElements', 0)
for key, value in {
    'Enabled1': 1, 'ElementShape1': 0, 'Name1': 'White Solid Fill',
    'PriorityBack1': 7, 'Opacity1': 1.0,
    'Red1': 1.0, 'Green1': 1.0, 'Blue1': 1.0, 'Alpha1': 1.0,
    'Enabled2': 1, 'ElementShape2': 2, 'Name2': 'Line Background',
    'Level2': 1, 'PriorityBack2': 4, 'Opacity2': 0.70,
    'Overlap2': 2,  # Composite, tested zero-based value
    'Red2': 0.02, 'Green2': 0.04, 'Blue2': 0.08, 'Alpha2': 1.0,
}.items():
    node.SetInput(key, value)
    actual = node.GetInput(key)
    if isinstance(value, (int, float)):
        assert isinstance(actual, (int, float)) and abs(actual - value) < 1e-6, (key, actual)
    else:
        assert actual == value, (key, actual)
for slot in range(3, 9):
    node.SetInput(f'Enabled{slot}', 0)
# Verify every used slot and name, save project; a human must confirm appearance.
```

**Border Fill grouping (user visually confirmed):** `Text` puts one continuous background behind the whole text element; `Line` gives each text line its own background (recommended); `Word` gives each word its own background; `Character` gives each glyph its own background. With `Opacity < 1.0`, overlapping Word/Character backgrounds can visibly darken the overlap regions. Prefer **Line** for conventional readable captions; use Word/Character only on explicit creative requirements. `Text Outline` and `Border Outline` are alternative optional decorations, not default background styles. 

**Text size and positioning:** In this tested workflow, **`Size = 0.1` is the recommended normal portrait-title baseline**, rather than `0.09` or the previous test's tiny `0.027–0.035`. Prefer inserting a fresh native Text+ **without changing `Size`**, read `node.GetInput('Size')`, and check it against the preferred `0.1` baseline for the installed build. Increase for a specific brief; avoid decreasing just to fit long labels. Shorten/reflow text or use more timeline sections instead. `Center` uses normalized Fusion coordinates (e.g. `{1: 0.5, 2: 0.68, 3: 0.0}`), **not pixels or track coordinates**; calculate/verify positions for each actual 9:16 canvas and check legibility and safe margins. Do not assume the above sample position always fits all fonts or line counts.

**When to use other styling:** Keep **one consistent foreground/background color pair across a video** unless the client requests otherwise. Use `Composite` blending as the baseline; `Solid` and `Transparent` exist in the Inspector but their API mappings and visual interactions were **not verified here**. True offset/blur drop shadows can use other Shading slots, but **do not enable them or rely on template defaults automatically**—a low/right default shadow often does little for readability. Offer/drop shadows only when specifically requested, with human review.

**Scope boundary:** Animated word-by-word spoken-word highlighting belongs to the **Subtitles** section, not this ordinary Text+ style recipe. A possible workflow is `Create Subtitles from Audio` → correct text/timing → use a native animated subtitle/word-highlight option where available → convert/rebuild as Text+ only if necessary for requested custom styling. **Do not claim those creation, word-timing, or subtitle-to-Text+ steps are Resolve API-automatable until separately tested.**

## 1.4. Fusion graph inspection, creation, maintenance

| Desired result | API | Evidence |
|---|---|---|
| Enumerate tools | `comp.GetToolList(False)` | [F/R] |
| Discover real input IDs and types | `node.GetInputList()`; inspect input `GetAttrs()` | [R] |
| Read/write an input | `node.GetInput(id, frame)`, `node.SetInput(id, value, frame)` | [D/F/R] |
| Add a positioned tool | `comp.AddTool('Merge', x, y)` | [T/R] |
| Rename a tool | `node.SetAttrs({'TOOLS_Name': 'Title_Merge'})` | [T] |
| Connect a graph input | `merge.ConnectInput('Foreground', title_node)` | [T/R] verify actual ID |
| Read/update Flow layout | `flow.GetPosTable(node)`, `flow.SetPos(node, x, y)` | [T/R] when CurrentFrame exists |
| Export / restore graph | `item.ExportFusionComp(path, 1)`; `item.ImportFusionComp(path)` | [T/R] inspect version signatures |
| Activate an imported comp | `item.LoadFusionCompByName(name)` | [T/R] |
| Discover Fusion tool registry IDs | `resolve.Fusion().GetRegList()` + each registration's `GetAttrs()` | [R] |
| Create 2D projective placement | `CornerPositioner` plus real numeric corner offset inputs | [R] |

```python
# [R] Inspect tools and title parameters before a write.
comp = item.GetFusionCompByIndex(1)
for node in comp.GetToolList(False).values():
    print(node.Name, node.ID)
    if node.ID == 'TextPlus':
        print(node.GetInputList())
        node.SetInput('StyledText', 'New editable title', 0)
        print('read-back:', node.GetInput('StyledText', 0))
```

**Readable Flow graph [T]:** main processing line left-to-right; inputs and masks on separate aligned lanes; `MediaOut` rightmost. Start with approximately **4/3 Flow units** between adjacent columns and rows, increasing by whole multiples for complex branches. Use descriptive **English** node names. Flow coordinates are unrelated to frame-image `Center` or timeline frames. If `CurrentFrame` is `None`, load/activate the composition and open Fusion; where unavailable, editing exported `.comp` `ViewInfo` followed by import is a **fallback requiring validation**, not an assumed universal method.

**Persistence [T/R]:** in some reported API builds, a newly assembled graph was not visible or did not survive a plain `SaveProject()`. A successful recovery was `ExportFusionComp` → `ImportFusionComp` → `LoadFusionCompByName` → Save/Close/Load. This is **a tested workaround, not proof every composition needs a round trip**. Verify nodes, connections, modifiers, representative rendered frames and alpha after reopening. `GetFusionCompCount()==1` alone can coexist with a broken/black image. Disconnect or bypass nodes diagnostically only in a duplicate, preferably with a saved known-good `.comp`.

## 1.5. Keyframes, Edit Inspector, Fusion Spline

**Default choice:** real `BezierSpline` keyframes for numeric values that a person may revise. `SetExpression('...time...')` evaluates a formula and does **not** create ordinary draggable Spline points. Expressions remain useful for constraints or procedural behavior.

```python
# [R] Seven real keyframes on a 254-frame native Text+ clip.
comp = title.GetFusionCompByIndex(1)
text = next(n for n in comp.GetToolList(False).values() if n.ID == 'TextPlus')
assert text.AddModifier('Size', 'BezierSpline')
for frame, size in [(0, .038), (42, .042), (84, .038),
                    (126, .042), (168, .038), (210, .042), (253, .038)]:
    text.SetInput('Size', size, frame)
spline = text['Size'].GetConnectedOutput().GetTool()
print(spline.GetKeyFrames())
```

**Confirmed Edit Inspector editing [R]:** A native Text+ title's `Inspector → Title → Text → Size` showed `0.042` at frame 42. Editing it to `0.043` **and committing the entry** (Tab) changed that exact keyframe; `GetInput('Size',42)` and `GetKeyFrames()` confirmed it, and the other six points stayed intact. The change was reverted and saved/reopened successfully. **This proves editing an existing keyframe value in Edit Inspector; it does not prove manual dragging of points in Fusion Spline or use of the Inspector diamond buttons.** A changed UI field without a committed value is not proof of a changed keyframe.

### Reusable numeric-animation helper — only for unanimated inputs

```python
# [S/R principle] Safe starting point for generating a NEW numeric animation.
def add_numeric_keys(node, input_id, points):
    input_obj = node[input_id]
    if input_obj is None:
        raise ValueError(f'Missing input: {input_id}')
    if input_obj.GetConnectedOutput() is not None:
        raise ValueError(f'{input_id} already has a modifier; preserve user animation')
    if not node.AddModifier(input_id, 'BezierSpline'):
        raise RuntimeError(f'Cannot add BezierSpline to {input_id}')
    for frame, value in points:
        node.SetInput(input_id, value, frame)
    output = node[input_id].GetConnectedOutput()
    if output is None:
        raise RuntimeError('Spline connection missing')
    return output.GetTool()
```

The original scripts used a shorter `keys(node, input_id, points)` helper without the existing-animation guard. **The guarded version above is proposed, not executed.** First test `GetConnectedOutput()` behavior on both a plain and an already animated input in the installed version. Never silently replace a person's keyframes; for intentional updates, inspect and preserve existing keys and modifiers and obtain approval for destructive regeneration.

**Other animation observations:** Numeric `Merge.Blend`, `Custom.NumberIn1/NumberIn2`, and `CornerPositioner` corner offsets were animated through `BezierSpline` [R]. For a compound `Center`/Point value, the agent used two numeric splines and a `Point(x,y)` expression as a *bridge* to editable keys; direct Point animation was not established as interchangeable. `TextPlus` Write On input IDs were `Start` and `End`, **not** `WriteOnEnd` [T]. Test BezierSpline on Start/End before promising editable Write On points [?].

**Per-character animation [F]:** `TextPlus.StyledText → StyledTextCLS → CharacterLevelStyling → BezierSpline` was used in earlier experiments. Generated keys were visible in Fusion Spline, but some manual-key deletion and `SetKeyFrames({}, True)` cleanup were unreliable in those tested conditions. Preserve starting character transforms and any user-created keys before regeneration. Text length changes can invalidate character indices; never clear the entire animation merely because an API call returned successfully.

## 1.6. Object separation, depth, text behind moving subjects

**Goal:** isolate a subject from its **original, uncut video**, when no alpha asset is supplied, and place an editable Text+ title behind that subject. Basic native layer logic:

```text
Foreground = original source masked to the subject
Middle     = TextPlus or other editable element
Background = original unmodified scene
Output     = Background → Middle → Foreground → MediaOut
```

Determine visibility and occlusion **through time**, not from track order alone. For a subject passing from behind a portal to the front, control foreground mattes and scene-depth transitions explicitly.

### Native Fusion DepthMap: tested depth image, not a reliable person alpha

```python
# [R] Resolve Studio 21.1.2.10: inspect registry IDs, not UI labels.
for entry in resolve.Fusion().GetRegList().values():
    attrs = entry.GetAttrs()
    label = ' '.join(str(attrs.get(k, '')) for k in
                     ('REGS_Name', 'REGS_UIName', 'REGS_ID'))
    if 'DepthMap' in label:
        print(label)

depth = comp.AddTool('DepthMap', 4/3, 0)
depth.ConnectInput('Input', comp.FindTool('MediaIn1'))
print(depth.GetInputList())
```

In the tested shot, `DepthMap` produced a real depth image, but also selected the foreground path and nearby trees: **not an isolated person matte** [R]. The registry also exposed a separate ResolveFX OFX DepthMap entry; do not confuse them. Available inputs included `DepthMapPreview`, `Mode`, `FarLimit`, `NearLimit`, `IsolateSpecificDepth`, `TargetDepth`, `Tolerance`, `Softness`, `ContractExpand`, `Blur`, and `DetailRecovery`. Optimal isolation with these controls remains [?].

`MagicMask` could be instantiated, and inputs such as `Strokes`, `TrackForward`, `TrackBidirectional`, `ReferenceTime`, `MatteBlur`, `ErodeDilate` were inspected [R]. `Strokes` is a `MagicMaskStrokes` data object, **not a Tool**. Programmatic stroke creation and tracking are **not confirmed** [?]. Compare with UI-assisted Magic Mask, Polygon/B-Spline roto, trackers, Delta Keyer, or Matte Control when depth alone is insufficient.

### Replaceable external matte fallback

An agent generated a grayscale PNG matte sequence with `u2net_human_seg.onnx` / ONNX Runtime while leaving the original video and Fusion nodes intact [R]. This is **intermediate mask media**, not a baked final shot. It has trade-offs: external-file dependency, possible hair/foot artifacts, and no native editable roto vertices. Keep source frame, FPS, duration, scale, and asset paths aligned; import may convert a `Loader` into `MediaIn`, with path available in `TOOLS_Clip_Path` rather than `GetInput('Clip')`.

```python
# [R] Grayscale PNG is not automatically an alpha channel.
# Both inputs must be time-aligned at matching image dimensions.
matte = comp.AddTool('Custom', 8/3, -8/3)  # actual ID is Custom, not CustomTool
matte.ConnectInput('Image1', original_frame_node)
matte.ConnectInput('Image2', grayscale_matte_node)
for key, expr in {
    'RedExpression': 'r1*r2',
    'GreenExpression': 'g1*r2',
    'BlueExpression': 'b1*r2',
    'AlphaExpression': 'r2',
}.items():
    matte.SetInput(key, expr)
```

**Matte temporal stability [?]:** The archived matte-generation script normalizes segmentation output **per frame**. This could produce frame-to-frame alpha/edge fluctuations, but no specific flicker failure was established. Before accepting a matte, preview the **moving sequence** at normal speed and inspect hair, hands, feet, motion blur, transparency changes, and edges on both light and dark backgrounds. Individual good-looking frames are insufficient. Improve/recreate only the matte when possible, without replacing the original video.

**Camera motion [R]:** SIFT/RANSAC homographies from a reference frame were encoded in `CornerPositioner` using true numeric X/Y BezierSpline keys. This approximates a perspective-aware **2D** warp, not a 3D camera solve. In one reported project/build, `CornerPositioner.UseGPU=0` removed a visible distorted top edge; `MotionBlur=0` alone did not. Apply this workaround **only after observing the artifact**. Limit a clean-plate overlay to the interval that actually requires subject removal; return to the original moving footage afterward. Clamp FastNoise values before thresholding procedural mattes, and verify actual opacity, not merely surface color.

## 1.7. Audio, transcription, color, stabilization

| Desired result | Available method / direction | Evidence |
|---|---|---|
| Place independent music, voice, SFX | `pool.AppendToTimeline([{'mediaPoolItem': audio_item, ..., 'mediaType': 2, 'trackIndex': audio_track}])` | [T/S] verify audio routing |
| Preserve editable sound | Keep distinct voice/music/SFX tracks; export mix only for delivery | [T] workflow |
| Native gain, EQ, fades, pan, Fairlight FX | Inspect installed `.pyi` and test isolated operation | [?] no complete verified API library |
| Lithuanian speech-to-text | `faster-whisper` with `language='lt'`; FFmpeg→PCM if necessary | [T] transcript still needs proofreading |
| Stabilize clip | `item.Stabilize()` | [T] used on 23 clips; inspect crop/artifacts |
| Apply editable Fusion-based color | Native Fusion `ColorCorrector` tool | [T] not the same as Color page grade |
| Apply Color page grades | `Timeline.CopyGrades`, `TimelineItem.SetCDL`, LUT/DRX pathways | [D/?] verify signatures and human editability |

**Audio:** inspect low-frequency rumble and defects before increasing gain. VAD and transcript timestamps may propose speech cuts, but review by listening; keep small margins around consonants and breaths. Avoid replacing the only active voice/music tracks with a single premixed WAV. If processing absolutely requires external audio stems, keep the stems independent and preserve source links.

**Color:** keep source media unchanged; apply corrections as editable Resolve/Fusion operations, not by generating a permanently graded video replacement. If the human must adjust a **Color page** grade, do not present a Fusion ColorCorrector as an equivalent editing experience. Visually verify subtle changes for natural skin tones and overall consistency.

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
})
job = project.AddRenderJob()
assert job
project.StartRendering([job])
```

A completed render job does **not** prove the output includes the expected video or audible audio. Use `ffprobe` to check actual streams, codecs, dimensions, FPS, duration, frame count and channels. Inspect frames and play back important cuts and transitions. After audio-only rendering, **reload the desired video preset** before creating the next job: a reported `Complete` MP4 contained no video until the preset was reset [T]. Do not assume `VideoQuality` values are accepted merely because the option appears in documentation.

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
- **9:16 scaling:** preserve aspect ratio and verify actual crop/important details on diverse source orientations. A universal version-specific Scaling API contract remains unverified.

**Color/Fusion bypass [T]:** A graph may exist but its effect or alpha may be bypassed. In one test, a controlled `Shift+D` in the **Edit** context changed the bypass state and fixed output; it is a *toggle*, not a command to press blindly. Validate viewer/export evidence, not only successful graph construction or `SaveProject()`.

---

# 2. Editing standards — what a human should find in the delivered project

1. **Editability over speed.** Native Text+ stays text, separately editable voice/music/SFX stay separate, color and composites remain non-destructive. A transparent MOV or premixed WAV is a fallback, not the default deliverable.
2. **Readable timeline.** Separate primary picture, occlusion/foreground, titles, dialogue, music and SFX when appropriate. Track order follows scene depth; sensible names and markers explain editorial intent. Do not accumulate abandoned test layers.
3. **English technical names.** Timeline, clip, track, Fusion nodes and compositions should have short, meaningful English names (`Opening_Title`, `Foreground_Matte`, `Voice`). Visible user-requested on-screen language remains unchanged.
4. **Text+ first for ordinary captions.** Prefer an individual native Text+ timeline clip, whose text and Size can be edited in the Edit Inspector. Use Fusion Composition for genuinely complex graph work; publish relevant controls where feasible. Keep default/native **Size around 0.1**, rather than shrinking to 0.09 or smaller without a specific reason. Maintain consistent foreground/background colors throughout a video unless the client specifies otherwise. For needed contrast, prefer native `Border Fill → Line`, **70% background opacity**, `Composite` blending, real names, and verified priority; avoid automatic shadows. Subtitles/word-level spoken highlighting are a separate workflow.
5. **Editable animation.** Prefer real keyframes for adjustable parameters. Inspector editing of native `Template.Size` is confirmed [R]; manual Fusion Spline dragging, more complex controls and existing-animation replacement need their own tests. Use expressions deliberately, with a clear reason.
6. **Readable Fusion node graph.** Left-to-right processing, organized mask/input lanes, consistent Flow spacing, descriptive names, MediaOut at the end. Preserve user-arranged graphs unless asked to reorganize them.
7. **Correct depth/occlusion.** Establish what should appear in front/behind and at what time. Try native DepthMap and Magic Mask as candidates, but verify the actual subject matte. A replaceable PNG matte sequence is acceptable only when the native path is insufficient and its dependency is documented. Text behind a person must remain editable Text+.
8. **Independent audio layers.** Keep voice, music, ambience and SFX independently adjustable. Do not bake color correction or dynamic effects into replacement video when native editing is available.
9. **Targeted changes.** Inventory the live timeline, export/duplicate before risky operations, and modify only the relevant items. Never recreate the whole cut to change one title. Respect manually edited keyframes and avoid duplicate timelines on reruns. Experimental test projects may be altered without backup **only when the user explicitly authorizes that**; production project protection is the default.
10. **Reliable script architecture.** Production scripts should have explicit functions, parameters and validated object references. **Do not reuse experimental patterns such as `exec(open('probe_feedback.py').read().split(...)[0])`:** they depend on another script's incidental text and make results fragile and hard to reproduce. Pin tool/model versions and keep test scripts separate from the maintained entry point.
11. **Verify persistence and appearance.** Save → close/load → read actual clip duration, Fusion nodes/connections, animation and media paths → inspect representative rendered frames. A valid API return or an Inspector text field is not a substitute for read-back. For procedural effects, report the exact frames and tolerances actually checked; do not claim universal pixel identity. Distinguish **API read-back**, **user-inspected appearance**, and **post-reopen persistence** as three separate evidence levels.
12. **Deliver a usable project.** Supply the editable project, independently reviewable render, meaningful track labels and a media dependency plan. `.drp` does **not** contain original sources, outside PNG mattes, or all Fusion Loader files. Review story logic in motion and sound, not just with a contact sheet.

**Suggested workflow:** live inventory/backup → minimal API/insert/title/render smoke tests → content and audio plan → native assembly → adjustable titles and animation → masking/depth work → independent audio and native color adjustments → save/reopen → technical + creative review → final export.

---

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

## Report new findings separately, not as a long appendix

After each new editing task, deliver a separate `RESOLVE_API_FINDINGS.md` with:
- **Newly verified operation:** Resolve build, exact API call/arguments, initial conditions, result/read-back, save/reopen outcome and human editability.
- **Unresolved operation:** the smallest concrete test that would distinguish competing explanations; do not turn a misunderstanding into an API limitation.
- **Proposed guide change:** only a reusable recipe or a short **X → Y → Z** warning, not a chronological debugging diary.

**Open research priorities:** (1) manually dragging/editing Fusion Spline keyframes; (2) Magic Mask stroke/tracking automation and finer DepthMap mattes; (3) native Fairlight and Color page automation; (4) safe precision trim/ripple without damaging other clips; (5) stable recovery, temporal matte quality and compositing verification; (6) Text+ Layout Circle/Path and other Blending modes; (7) editable, time-aligned subtitles/word highlighting and API access.

**Provenance / follow-up references:** `RESOLVE_AGENT_GUIDE_feedback_1.md`, `STARGATE_V3_API_FINDINGS.md`, `TEXTPLUS_INSPECTOR_ANIMATION_V4.md`, `Resolve_Agent_Playbook_v0.1.1.md`, `MONTAVIMO_PATIRTIS_IR_PATOBULINIMAI.md`, `RESOLVE_AGENT_GUIDE_feedback_v1.2.md`, the user-supplied November 2026 `rebuild_shading_samples.py` code and screenshots, the prior `darbas-prie-efekto_20261027_0258.json`, and selected scripts inside `resolve agent roadmap.zip`. For API verification use the **installed** `Developer/Scripting/README.md`, `DaVinciResolveScript.pyi`, Fusion scripting references, and the active MCP tool descriptions. Public background references: https://wiki.dvresolve.com/developer-docs/scripting-api and https://documents.blackmagicdesign.com/UserManuals/Fusion8_Scripting_Guide.pdf.

*This is an operational guide, not a universal executable script. Every result remains conditional on the installed Resolve version and actual state/visual read-back.*
