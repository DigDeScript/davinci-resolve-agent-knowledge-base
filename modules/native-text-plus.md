# Native Text+ titles, sizing, Shading, editable captions

> **21.2 compatibility:** this module preserves earlier recipes and evidence. For current signatures, newly tested operations and restrictions, read [Resolve 21.2](resolve-21.2.md). Older `GetProperty`/`SetProperty` and `GetSetting`/`SetSetting` examples require the current dictionary forms.


> [Back to GUIDE.md](../GUIDE.md) | Evidence keys and general safety: [setup-and-safety.md](setup-and-safety.md)

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

**Scope boundary:** Word-by-word highlighting is a **native subtitle-track effect** and is implemented separately. See [word-highlight.md](word-highlight.md). Native `CreateSubtitlesFromAudio()` has been exercised in prior tests, and the user has verified that manually generated native captions pick up a Word Highlight effect already installed on an empty subtitle track. No universal per-word timing edit API is established.
