# AV pairing, trim and synchronization

> **21.2 compatibility:** this module preserves earlier recipes and evidence. For current signatures, newly tested operations and restrictions, read [Resolve 21.2](resolve-21.2.md). Older `GetProperty`/`SetProperty` and `GetSetting`/`SetSetting` examples require the current dictionary forms.


> [Back to GUIDE.md](../GUIDE.md) · [Timeline/timebases](timeline-and-media.md) · [Render QA](render-and-qa.md)

**Use when:** inserting, trimming or moving original picture/sound pairs; adding audio transitions; diagnosing a suspected sync problem. For a normal montage, preserve the original relationship and use the short recipe. Run deeper diagnosis only when something fails or a mismatch is reported.

**Current evidence:** the original-pair insertion, linked trim/move, gain, audio fade and transition sequence was independently exercised on Studio 21.2.0.5 in an isolated project copy. See [exact results and limits](resolve-21.2.md#av-operations-and-persistence). The earlier 21.1.2 audit confirmed 40 production pairs but did not rerun mutations. Neither session establishes perceptual sync. Other builds, retimed/multicam clips and separate-recorder material need their own bounded tests.

## 1. Prove one original AV pair before a batch

Preconditions: protected working/test timeline, identified MediaPool source with picture and sound, known source/timeline FPS, a free destination interval, and enough source material around both edges. This recipe covers an ordinary 100% speed pair, not intentional J/L cuts or externally synchronized recordings. Obtain audio items by source identity and actual linkage/placement; do not pair clips merely by list order or name.

| Operation | Exact API pattern from local definitions/reported use | Verify before continuing |
|---|---|---|
| Insert original AV | `pool.AppendToTimeline([{'mediaPoolItem': source, 'startFrame': source_in, 'endFrame': source_out, 'recordFrame': destination, 'trackIndex': 1}])` | Source-frame arguments and absolute timeline destination are different units. No `mediaType` restriction in this reported AV path. Discover both created members; the returned list need not contain both. Confirm source identity, duration and destination of each. |
| Establish relationship | `timeline.SetClipsLinked([video, audio], True)`; read each `GetLinkedItems()` | Both members identify each other; compare their actual source mapping, timeline edges and speed. Linking alone does not repair an existing offset. |
| Shorten the left edge | `video.SetLeftOffset(video.GetLeftOffset() + trim_frames, False, True)` | This pattern increases the available left handle and shortens the pair in the reported case. `False` selects whole-frame precision; `True` updates linked items. Confirm BOTH members changed as intended and the duration decreased by the expected amount. |
| Shorten the right edge | `video.SetRightOffset(video.GetRightOffset() + trim_frames, False, True)` | Same paired read-back, now at the right edge. Do not supply an absolute source-frame index as the offset. |
| Move the pair | `timeline.MoveItems([video, audio], {'startFrame': destination}, False)` | Here `False` disables adding other linked items automatically; both selected members are explicitly supplied. Confirm equal destination shift, unchanged source ranges/speed, and no collision with other items. |
| Add a needed audio transition | `audio.AddTransition({'type': 'Cross Fade +3 dB', 'category': 'audio', 'position': 'end', 'alignment': 'center', 'duration': transition_frames})` | This is a locally reported type, not the default choice for every sound. Confirm the intended adjacent audio clip, adequate handles on both sides, returned transition type/placement/duration and actual sound. |
| Save and reopen | `pm.SaveProject()` → protected close/load → reacquire references | Compare the measured pair and transition state before/after. Check the result in playback. A successful call is only the first check. |

**Trial sequence:** insert → read pair → trim one edge → read pair → move → read pair → add a transition only if needed → listen → save/reopen → compare. Try representative source rates, e.g. both 30 and 29.97 if present. If a step fails, stop that batch and recover the known working state; do not continue from half a paired edit. Remove only identified test artifacts when authorized, not all clips on a track.

The offset methods are documented as available extension in frames. The installed comments do not fully settle every mixed-FPS case. Verify their operational timebase on the test pair before computing changes from seconds; if it is not established, use native trim controls with read-back. The patterns above are a test recipe, not a universal ready-to-run script.

## 2. Small checks that prevent large errors

- **Read the actual end.** In the archived trial, requested source `[60, 360)` produced 300 timeline frames for one 29.97 source and 299 for one 30 fps source in a 29.97 timeline. Position the next segment from the actual `GetEnd()`; do not force nominal arithmetic by independently stretching audio or video. This observation is not a general rounding formula.
- **Keep source indexes and handles separate.** One local case reported `GetSourceStartFrame() = 4008` and `GetLeftOffset(True) ≈ 4003.996`. Record both; never compare them as if they shared a unit. Source time, absolute timeline time and available extension answer different questions.
- **Include fractional audio positions.** `GetStart(True)`, `GetEnd(True)` and offsets with `True` expose subframe information in this build. Check the precision and tolerance appropriate to the operation. Matching rounded integers can hide a fractional shift.
- **Check relationships explicitly.** Compare stable source/media IDs, source ranges, timeline ranges, speed and reciprocal link IDs. For a previously offset/synchronized pair, preserve the intended relative mapping rather than forcing equal in-points. An ordinary same-source pair has the simpler equal-range expectation.
- **Transitions need real content outside the cut.** A centered transition borrows source material on both sides. Read actual placement/handles and inspect that material for silence, unwanted syllables or an unrelated sound. Do not assume half the requested duration always describes the actual support, especially with odd lengths or mixed rates.
- **Separate clip and transition items.** `GetItemListInTrack()` in this build includes transition items. Filter by `GetType()` for pair checks; inventory transition objects separately. Intentional transition overlap is not an accidental primary-clip overlap.
- **Trim before transitions where practical.** If revising an already transitioned edit, inspect affected transition behavior and source handles again. Refresh the manifest and relevant audio/render QA after the change.

## 3. Diagnose sync by finding where the difference appears

1. Pick a clear visible and audible event: a visible impact with a short sound, or clearly articulated speech with visible lips. Record its location and the observed direction/size of any offset. Do not infer it from different FPS labels.
2. Check that same event in the original file, an untouched Resolve AV pair, and the edited pair. Use more than one event along the clip if drift is suspected. For a long edit, include beginning/middle/end and each relevant source type.
3. If the source and untouched pair already show the same offset, investigate the source or playback/decoding path before changing the edit. If it appears only after an edit, compare its exact before/after ranges, speed, source mapping and fractional audio position.
4. Compare playback with a short synchronized Resolve render when the playback path itself may be responsible. Check source timestamps/VFR interpretation only as a hypothesis until an event comparison localizes the difference.
5. Apply a correction only to a measured, repeatable problem, on a protected copy. Recheck the same events and check for new drift. Document what was changed and why.

**Three different conclusions:** matching structure → “no independent positional change found”; waveform correlation → “rendered audio matches source at these sampled times”; audiovisual review → “these visible/audible events were checked for sync.” None implies the others automatically, and a few events do not prove every frame.

The archived audio comparison checked 120 interior windows against a previously rendered timeline WAV and reported at most 0.067 **ms** difference, with correlations about 0.79–1.00. At 16 kHz one sample is 0.0625 ms: this is an audio alignment measurement near the analysis sample grid, not sub-millisecond proof of lip sync. Reuse it only when the render is known to match the current timeline revision. Interior samples do not test every transition or the video's timing.

With audio crossfades, local `GetSourceStartTime()` / `GetSourceEndTime()` readings differed from picture by amounts consistent with transition support. Do not diagnose a whole-clip slip from that difference alone. If it matters, compare the same test pair with and without a transition, preserving an unchanged reference.

## 4. Source edges and persistence

For suspected silent heads/tails, record file/stream identity, sample rate, channel, threshold, window length, first/last active time and stream start times. Analyze each channel for diagnosis; mono downmix can hide channel differences or cancellation. A 0.35 s minimum silence setting cannot be expected to detect a 0.27 s interval. Select a shorter diagnostic interval for short defects and retain the parameters with the result.

The local report's 0.27–0.35 s near-silence finding is supported by 16 kHz mono, 10 ms block analysis; it does not by itself establish the cause, audible harm, or an AV offset. The existing `silence_probe.py` can flag candidate low-level intervals with adjusted parameters but is **not** a per-channel edge audit. No `audio_edges_probe.py` is bundled yet. If a passage is unusable, exclude it with its original AV relationship intact; do not slide only the audio to fill the quiet head.

The earlier agent reported that video `SetFades({'FadeIn': 0, 'FadeOut': 8})` read back correctly immediately but reset after reopening. A native end `Cross Dissolve` (`category='simple'`, `position='end'`, `alignment='left'`, `duration=8`) was the reported alternative. The current audit found that transition and current exported frames show the closing dimming. The disappearance was subsequently independently reproduced on 21.2.0.5; the existing native ending transition survived the protected project reopen. See the current-version test record. Test your own build and inspect the intended fade; do not automatically replace every video fade.

For persistence, retain actual before/after values for ranges, speed, links, gains, fades and transitions. Store the comparison and mismatches, not only `saved_reopened: true`. A snapshot that contains clip edges but omits gain/fades cannot prove those omitted properties survived.
