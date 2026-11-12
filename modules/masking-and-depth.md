# Masks, DepthMap, Magic Mask, external matte, occlusion

> **21.2 compatibility:** this module preserves earlier recipes and evidence. For current signatures, newly tested operations and restrictions, read [Resolve 21.2](resolve-21.2.md). Older `GetProperty`/`SetProperty` and `GetSetting`/`SetSetting` examples require the current dictionary forms.


> [Back to GUIDE.md](../GUIDE.md) | Evidence keys and general safety: [setup-and-safety.md](setup-and-safety.md)

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
