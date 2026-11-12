# Setup, discovery, evidence, project protection

> **21.2 compatibility:** this module preserves earlier recipes and evidence. For current signatures, newly tested operations and restrictions, read [Resolve 21.2](resolve-21.2.md). Older `GetProperty`/`SetProperty` and `GetSetting`/`SetSetting` examples require the current dictionary forms.


> [Back to GUIDE.md](../GUIDE.md) | Evidence keys and general safety: [setup-and-safety.md](setup-and-safety.md)

**Source:** Original guide v1.2, modularized as v1.3 on 2026-11-02. Prioritize a correct, intelligible, **human-editable Resolve project**, not merely a finished MP4 or the fastest workaround.

**Evidence environment:** Reports and archived scripts from DaVinci Resolve **Studio 21.1.2.10**, Windows, Python 3.13. This guide consolidates those observations plus the user-reviewed November Text+ Shading rebuild. Those historical consolidation sessions did not rerun the commands. The 1.7 release separately tested a bounded set of operations on 21.2.0.5; see [current evidence](../evidence/resolve-21.2.0.5.md). Check your installed API before relying on behavior in another build.

**Evidence labels:**
- **[R]** Reported working with read-back, render, user visual inspection, or save/reopen evidence from the editing agent; check the specific assertion made.
- **[T]** Reported as tested by an earlier editing agent, without independent reproduction here.
- **[F]** Observed in the earlier Fusion / ExplodingText experiments.
- **[S]** Exact use appears in the archived Python scripts; successful runtime behavior was not separately reverified here.
- **[D]** Appears in documented/local API definitions; the particular workflow still needs testing.
- **[?]** Hypothesis or unverified workflow. **Never present it as a tested solution.**

**Non-negotiable rule:** Prefer native, nondestructive Resolve operations. Keep text, animation, sound, color, and compositing editable. Use rendered intermediate media only for a justified purpose; record what cannot be edited afterward. Validate actual project state and output, not only API return values.



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
