# Rotating a soft Square gradient with native keyframes

**Status:** locally tested by the proposing agent, not independently validated. Studio 21.2.0.6, Windows, Python 3.13.5; 1080 × 1920 and 1920 × 1080 timelines, square pixels, 30 fps, 630 frames. This is a background technique, not a change to the title effect.

[Fusion reference](fusion-and-animation.md) · [Render and QA](render-and-qa.md) · [Known traps](known-traps.md)

## Use a separate Transform for rotation

The tested Background tool exposes `GradientType='Square'` and Start/End points, but no dedicated gradient-rotation angle. Its other settings (for example ShutterAngle) are not an orientation control. A native Transform makes rotation accessible through its ordinary **Angle** control and editable Spline keys.

The tested processing order is:

`Background → Transform → Crop → ChangeDepth → existing background composites`

Keep titles, UI/progress decorations and other elements outside this rotating branch. Connect the cropped background to the existing composition's background input. Do not rotate the final flattened image unless all its contents should rotate.

## Overscan before rotating, crop afterward

Rotating a frame-sized rectangle can reveal transparent corners. For a centered, unit-scale rotation into a W × H square-pixel output, create a square source with side at least `sqrt(W*W + H*H)`, plus a small sampling margin. This encloses the output rectangle at every angle. Different pivots, translation, scale or pixel aspect require a new coverage calculation.

For both tested Full HD orientations the source side was:

```python
side = math.ceil(math.hypot(width, height) / 16) * 16 + 16  # 2224 pixels
```

Set Background `UseFrameFormatSettings=0`, `Width=Height=side`, `PixelAspect=(1,1)`, `Type='Gradient'`, `GradientType='Square'`, and opaque color stops. Center the gradient and Transform pivot. The tested gradient had Start `(0.5,0.5)` and End `(0.92,0.5)` on this square source. Set Crop `XSize=W`, `YSize=H`, `KeepCentered=1`, `ClippingMode='Frame'`. The Crop output, not the overscan generator, should determine the downstream background resolution.

Also verify the timeline-item duration, composition Render/Global ranges, and Background GlobalIn/GlobalOut. A correct timeline length alone does not prove a newly created generator covers the whole range. Do not animate Crop size for this effect.

## One turn with two keys

Use actual Fusion-local RenderStart/RenderEnd. In the tested 630-frame composition those were 0 and 629. Put Angle 0 degrees at frame 0 and 360 degrees at frame 629, with linear interpolation. This is one complete turn from the first to the last visible frame. It is not an instruction to use frame 630 as the last visible key.

Example for a newly created, unanimated Transform in an authorized disposable or generated composition:

```python
assert rotate['Angle'].GetConnectedOutput() is None  # preserve existing user animation
assert rotate.AddModifier('Angle', 'BezierSpline')
spline = rotate['Angle'].GetConnectedOutput().GetTool()
result = spline.SetKeyFrames({
    first: {1: 0.0, 'Flags': {'Linear': True}},
    last:  {1: 360.0, 'Flags': {'Linear': True}},
}, True)
if result is False:
    raise RuntimeError('Keyframe setter rejected the operation')
for frame in [first, first + (last-first)//2, last]:
    expected = 360.0 * (frame-first) / (last-first)
    assert abs(rotate.GetInput('Angle', frame) - expected) < 1e-7
```

In this trial SetKeyFrames returned None even though the keys were installed. Read-back showed collinear Bezier handles, rather than retained Linear flags; intermediate Angle values established constant speed. Do not infer a failed or correct animation from the setter return alone. A centered Square gradient has fourfold symmetry: similar pictures repeat about every 90 degrees even though the Angle completes only one 360-degree turn.

## Separate gentle color falloff from quantization banding

These are different problems:

- **Abrupt tonal falloff:** distribute the same endpoint colors over a gentler ramp. The tested background used 33 stops at `u=i/32`, with color mixing fraction `s=6*u**5-15*u**4+10*u**3`. Each color is `inner + (outer-inner)*s`; alpha stays 1. This eases the endpoints of the color ramp, not the rotation speed. The stops are generated once and remain a native static gradient. To change both endpoint colors while retaining this ramp, regenerate the stops; changing just one of the 33 stops is a different curve.
- **Visible quantization bands:** generate/process the background in float (`Background.Depth=4`, float32), then reduce it through `ChangeDepth.Depth=1` (int8), `Dither=1` (Error Diffusion) immediately before the existing background composites. Dither has an effect when reducing depth; enabling it at Keep or while increasing depth does not perform this conversion. This int8 choice targets an SDR 8-bit deliverable, not an HDR/high-bit-depth master.

The tested palette was intentionally dark. Dither changed 1,211,626 of 2,073,600 pixels at sampled portrait frame 79, with mean absolute channel difference 0.25475 and maximum difference 1 code value versus the same conversion without dither. This establishes that the stage affected quantization subtly; it does **not** prove that every codec, bitrate or display will retain it. Inspect the actual delivery encode: compression can remove fine dither. Do not route foreground titles through this reduction unnecessarily.

## Reproduction and verification coverage

1. In an authorized synthetic/generated background, construct the chain and bounds above. Use named tools and a left-to-right Flow layout.
2. Export samples at local frames 0, 79, 157, 236, 315, 472 and 629; inspect corners, aspect ratio, rotation and foreground independence. The trial used both portrait and landscape dimensions.
3. Read Angle at 0/79/157/315/472/629: observed 0 / 45.214626 / 89.856916 / 180.286169 / 270.143084 / 360 degrees, within 1e-7 of linear motion.
4. Save, close and reload, reacquire references and read the same controls. The trial retained Square, float depth, dither, dimensions and rotation values; the composited frame 60 was pixel-identical before/after reopen in both formats.
5. Render the actual deliverable and inspect it separately. Native image exports and input read-back do not constitute full motion playback or perceptual audio review. This background recipe does not change the audio.

The 2224-square float source contains about 2.39 times as many pixels as one 1920 × 1080 frame. Budget memory/rendering accordingly; no universal performance improvement is claimed. Motion blur, HDR delivery, non-square pixels, different pivots and other Resolve builds were not tested. No private project, client media or rendered image is included with this proposal.
