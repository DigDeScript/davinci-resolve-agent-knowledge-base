# Fusion graphs, keyframes, expressions, layout

> **21.2 compatibility:** this module preserves earlier recipes and evidence. For current signatures, newly tested operations and restrictions, read [Resolve 21.2](resolve-21.2.md). Older `GetProperty`/`SetProperty` and `GetSetting`/`SetSetting` examples require the current dictionary forms.


> [Back to GUIDE.md](../GUIDE.md) | Evidence keys and general safety: [setup-and-safety.md](setup-and-safety.md)

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

## External Fusion macro/animation references (v1.6)

The [AutoSubs Fusion skill](https://github.com/tmoroney/auto-subs/blob/main/.agents/skills/davinci-resolve-fusion/SKILL.md) organizes knowledge of `BezierSpline`, keyframe handles/easing, `StyledTextFollower`, `.setting` macro files and Inspector-exposed inputs. It documents a significant serialization distinction: `SetKeyFrames()` handle coordinates are **relative**, while `.setting` file handles are **absolute**. The distinction has not been independently reproduced in this Resolve Studio 21.1.2.10 setup.

Macro published controls may involve internal `UserControls` and externally exposed `InstanceInputs`; stored Inspector layout and currently instantiated macros may differ after adding controls. `KeyStretcherMod` can be relevant to length-independent reusable animations, but its behavior remains exploratory for our Text+ templates.

These concepts supplement the proven Word Highlight DRT holder and do not change or replace that effect asset.
