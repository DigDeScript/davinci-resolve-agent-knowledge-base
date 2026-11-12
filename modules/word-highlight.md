# Native Word Highlight subtitles — independent project workflow

> **21.2 compatibility:** this module preserves earlier recipes and evidence. For current signatures, newly tested operations and restrictions, read [Resolve 21.2](resolve-21.2.md). Older `GetProperty`/`SetProperty` and `GetSetting`/`SetSetting` examples require the current dictionary forms.


> [Back to GUIDE.md](../GUIDE.md) | Asset: [`../assets/word_highlight.xml`](../assets/word_highlight.xml) | Tool: [`../tools/word_highlight.py`](../tools/word_highlight.py)

**Status:** Tested on DaVinci Resolve Studio **21.1.2.10**, Windows, November 2026. The user visually confirmed native Word Highlight with correct word-by-word synchronization, transparent background, and both requested colors in a timeline created from an **effect-free** source. A separate new-project test confirmed that native subtitles can be generated **after** a Word Highlight effect is already installed on an empty subtitle track. The packaged `word_highlight.py` was subsequently used successfully **end-to-end in a new Resolve project** by an independent agent (2026-11-02), including a second run with a new requested palette, native captions and render verification. This confirms the workflow in the tested build only, not a universal Resolve API guarantee.

## Decision: which subtitle workflow?

- **Native, word-synchronized animated subtitles** requested → use this module. The effect is attached to a **subtitle track**, not each caption clip or a Text+ object.
- **Ordinary editable labels, on-screen headings, marketing captions** → use [native-text-plus.md](native-text-plus.md), not this module.
- New project without subtitles → create **one empty subtitle track**, install effect, then generate native subtitles from audio. This order was visually tested.
- Existing project with native subtitles on one subtitle track and **no effect** → install effect into that track, preserving caption clips.
- Multiple subtitle tracks, an existing Fusion effect holder, unsupported DRT structure, or a missing template → stop and report; avoid inventing an unsafe transformation.

## Prerequisites

1. Resolve scripting enabled, current project containing the source video/audio and at least one timeline. See [setup-and-safety.md](setup-and-safety.md).
2. Local **entire `Resolve_Agent/` folder** available to the agent, not only GUIDE.md; specifically `assets/word_highlight.xml` and `tools/word_highlight.py`.
3. Working `python` 3 with standard library; **no external Python packages** needed for offline DRT editing.
4. Installed Resolve version and native caption-generation language support checked at runtime. Example API constants below are for **English**; do not label another language as English merely to force automation.
5. Preserve the original timeline. Export to an unused, distinct `.drt` filename; install tool deliberately refuses to overwrite output.

## Proven donor asset

`assets/word_highlight.xml` contains the **actual unmodified** `<FusionCompHolderItems>` XML extracted from the user-supplied `WH_Before_Subtitles_Test.drt` (with 12 generated native subtitle clips). The asset contains **the effect holder only**, not those clips. Its SHA-256 without trailing newline:

`658581d6c02353776b7e486133a64b7a85d1b2467b9698614ae351c4d287cb76`

The **asset is a proven donor holder**, not the desired default user-facing palette. The CLI now defaults to the original native Word Highlight colors: **normal `#FFEB85`**, **active word `#FF0000`**. These values are applied when `--normal` and `--highlight` are omitted. If a task specifies colors, pass them explicitly.

Known **asset** configuration (preserved as tested):

| Purpose | Fusion macro channels | Expected color |
|---|---|---|
| Normal subtitle text | `Red1` (implicit default `1`), `Green1 = 0`, `Blue1 ≈ 0.52156862745098` | `#FF0085` |
| Active word | `HighlightColorRed = 0`, `HighlightColorGreen ≈ 0.666666666666667`, `HighlightColorBlue = 1` | `#00AAFF` |

The effect's preset ID is `Templates/Edit/Titles/Subtitles/Animated/Word Highlight`. **Do not confuse** native Text+ shading values and these Fusion macro color controls.

## Procedure: new video, no captions yet

### 1. Create an untouched source and an experimental working timeline

Connect to Resolve; inventory project/timeline and video/audio; duplicate the source timeline using `DuplicateTimeline(...)` and activate the duplicate. If the duplicate has no subtitle track, create exactly one with `timeline.AddTrack('subtitle')`. Verify with `GetTrackCount('subtitle') == 1` and that `GetItemListInTrack('subtitle', 1)` is empty.

Keep the original video and audio clips unchanged. Do **not** generate captions yet.

### 2. Export the working timeline's DRT

```python
# Variables: resolve, project, working (current working timeline).
from pathlib import Path
pre = Path(r'C:\path\to\work\before_word_highlight.drt')
assert not pre.exists()
assert working.GetTrackCount('subtitle') == 1
assert not (working.GetItemListInTrack('subtitle', 1) or [])
assert working.Export(str(pre), resolve.EXPORT_DRT, resolve.EXPORT_NONE)
```

If the DRT has no `<SubtitleTrackVec>` or cannot retain an empty subtitle track, stop and investigate instead of faking captions.

### 3. Insert holder and configure RGB offline

From the root `Resolve_Agent/` folder:

```powershell
python tools/word_highlight.py inspect
python tools/word_highlight.py install --input "C:\path\to\work\before_word_highlight.drt" --output "C:\path\to\work\with_word_highlight.drt" --normal "#FF0085" --highlight "#00AAFF"
python tools/word_highlight.py inspect-drt --input "C:\path\to\work\with_word_highlight.drt" --expect-normal "#FF0085" --expect-highlight "#00AAFF"
```

The tool installs into exactly **one existing subtitle track**, which must not already contain an effect. It preserves media references, timeline content, and caption clips. It handles **existing** RGB inputs and the known implicit red default. Adding an arbitrary **missing** Fusion color input (e.g. `Red1` to force normal text red below `255`) has **not** been validated: the tool intentionally stops with an error rather than pretending that all HEX values are supported. The proven example colors are fully supported. The new original-style defaults `#FFEB85` and `#FF0000` use existing serialized color inputs and the implicit normal-red default, so they do not require unsupported input insertion.

### 4. Import exactly one new timeline

```python
result = project.GetMediaPool().ImportTimelineFromFile(str(
    Path(r'C:\path\to\work\with_word_highlight.drt')))
assert result is not None
assert result.SetName('WordHighlight_Final_Test')
assert project.SetCurrentTimeline(result)
```

Always verify new timeline ID, original source timeline still present and unchanged, video/audio item inventory, native subtitle track count, and DRT holder existence. The API creates a **new timeline**; it is not an in-place modification. Do not delete staging or original timelines automatically.

### 5. Generate native captions *after* installation

Before recognition, identify the **actual language of the source audio** rather than defaulting to `Auto`; if unavailable in the short list, look for **Enable Extended Language Support** in Resolve's transcription settings and confirm language-pack availability. A prior edit produced unrelated English words when `Auto` identified the wrong language. Do not use invented captions or pretend an unsupported language is available through the native API. Use the native Resolve caption-generation API with the installed build's actually supported options. **The following is an English-only example, not a universal default:**

```python
settings = {
    resolve.SUBTITLE_LANGUAGE: resolve.AUTO_CAPTION_ENGLISH,
    resolve.SUBTITLE_CAPTION_PRESET: resolve.AUTO_CAPTION_SUBTITLE_DEFAULT,
    resolve.SUBTITLE_CHARS_PER_LINE: 30,
    resolve.SUBTITLE_LINE_BREAK: resolve.AUTO_CAPTION_LINE_DOUBLE,
    resolve.SUBTITLE_GAP: 0,
}
ok = result.CreateSubtitlesFromAudio(settings)
print('Caption creation accepted:', ok)
# Depending on build, poll project.GetCreateSubtitlesFromAudioStatus()
# until completion; inspect newly created caption clips and tracks.
```

**Evidence boundary:** initially the user manually generated captions after installation and verified synchronization. Subsequently an independent agent followed the packaged guide in a new project and successfully performed the complete automated path twice, generating **85** native English caption blocks and validating their DRT structure. Other languages and Resolve builds remain unverified.

**Important:** Resolve could place newly generated captions on another subtitle track. Verify that the caption items and effect holder are on the **same** track. If not, stop and report, rather than silently regenerating or moving effects.

### 6. Validate after generation

- Check `GetTrackCount('subtitle')` and actual native captions using `GetItemListInTrack('subtitle', i)`.
- Export the newly generated timeline as a **new** DRT and run `inspect-drt` with expected colors.
- Compare source media, edit length, frame rate and caption timing with the intended input timeline.
- Verify Fusion XML holder, both complete zlib streams/checksums and **all three length headers**.
- **Visual check**: captions appear at the right times, one word highlights at a time, normal/highlight colors are correct, background transparent, no black images. Playback and Console observations may require the user in restricted computer-use environments.
- Save project; report what was checked automatically vs visually.

## The critical DRT serialization fix

`CompositionBA` is HEX-encoded binary inside the subtitle-track effect holder. The observed working format has **two zlib layers and THREE length headers**:

| Header | Location | Endianness | Required value |
|---|---|---|---|
| Outer uncompressed length | First 4 bytes of `CompositionBA` binary | Big-endian | `len(outer)` |
| Embedded outer payload length | Offsets **142–145** of *decompressed outer* payload | Big-endian | `len(outer) - 146` |
| Inner uncompressed length | Four bytes immediately before inner zlib stream (`78 DA`) inside outer payload | Little-endian | `len(inner)` |

Safe reconstruction: decompress outer → locate/validate unique inner stream → modify explicit `Tools.Template.Inputs` value → zlib-compress inner (level 9) → update inner length → update embedded length → zlib-compress outer (level 6) → update outer length → revalidate both streams, checksums and input values. The sample tool implements these steps. Do not add raw bytes, fake lengths, or assume unchanged compressed size.

**Evidence:** A failed import of `Green1: 0.92 → 0.00` preserved only **3,081 of 3,083** decompressed outer bytes because the embedded header remained stale at 2,935. After correcting that header to 2,937, import, re-export, complete zlib checks and user playback all succeeded. Changes to `HighlightColorBlue` likewise succeeded. Effect transfer into an effect-free timeline and later subtitle generation on an effect-bearing empty track both worked visually.

## Known limitations and logs

- The binary/XML layout is a reverse-engineered observation from **Resolve 21.1.2.10**, not a public stable file-format guarantee. The tool fails closed on unexpected structures.
- `UpdateWordAnimation` Lua warnings appeared when the user manually clicked color and confirmed OK even in an untouched, non-DRT-imported timeline. They were **not** correlated with broken playback; do not claim they prove DRT corruption. Inspect actual behavior.
- The missing-input insertion (`Red1 ≠ 1`) remains untested; the tool reports and stops. Do not conceal this limitation.
- Native subtitles do not automatically imply a publicly exposed API for precise **per-word text/timing edits**. Preserve native word timing wherever possible.
- Do not run the earlier experiment-specific `word_highlight_before_subtitles_generate.py` against a timeline that already has subtitles: it explicitly asserts that the track is empty and has a hard-coded project name. Follow this module's live-project procedure instead.
- For timeline/DRT backups: a DRT references external source media. It is not a standalone media archive.

## Existing track: changing colors without losing corrections

The current `install` CLI **refuses to overwrite** a subtitle track that already has an effect holder. It does **not** expose a supported `recolor` command; never claim otherwise. When changing a palette, preserve user-corrected native subtitle text and timings:

- Work in a duplicate. Prefer a clean subtitle track with the same clips but no existing holder; export its DRT, install the requested colors, then import a new timeline.
- Where safe and user-authorized, remove the Word Highlight **track effect** in the duplicate using Resolve UI and retain the subtitle clips; export that clean DRT and install the replacement effect. **Do not regenerate corrected captions solely to recolor.**
- Re-export, verify all caption text and timing digests and colors, and check visual playback. If the clean track cannot be obtained without affecting subtitle data, stop instead of overwriting a serialized holder blindly.
- **Future work (not implemented):** an atomic `recolor` command that edits an existing holder without touching the native caption clips, plus outline/background color and geometry controls. Their serialized mapping has **not** yet been analyzed and must not be guessed.

## CLI summary

```text
python tools/word_highlight.py inspect [--asset PATH]
python tools/word_highlight.py inspect-drt --input FILE.drt [--expect-normal #RRGGBB] [--expect-highlight #RRGGBB]
python tools/word_highlight.py install --input BEFORE.drt --output AFTER.drt [--asset PATH] [--normal #RRGGBB] [--highlight #RRGGBB]
```

When `--normal` or `--highlight` is omitted, defaults are **#FFEB85** and **#FF0000** respectively. The example above explicitly uses the earlier experimental palette, not the defaults.

The CLI performs **offline file transformations only**. Resolve Python or MCP is still needed for creating tracks, exporting/importing timelines, generating captions and saving the project. Never describe an offline DRT generation as a completed Resolve editing task.
