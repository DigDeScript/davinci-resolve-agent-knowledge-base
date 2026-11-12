# Editorial strategy: transcript-led vs visual-story-led editing

> **21.2 compatibility:** this module preserves earlier recipes and evidence. For current signatures, newly tested operations and restrictions, read [Resolve 21.2](resolve-21.2.md). Older `GetProperty`/`SetProperty` and `GetSetting`/`SetSetting` examples require the current dictionary forms.


> [Back to GUIDE.md](../GUIDE.md) | Related: [Timeline and media](timeline-and-media.md), [Audio and color](audio-and-color.md), [Render and QA](render-and-qa.md)

**Purpose:** Choose a suitable editing method before assembling the timeline. Transcript-driven selection helped condense an 18:56.5 educational source to 2:57.6 (15 segments, 85 native subtitle blocks) on 2026-11-02. A separate 49.5-second personal/walk reel was assembled technically but required significant human revisions to shot selection and speech cuts. These are task-specific reports, **not** proof of reliable semantic or phonetic accuracy.

## 0. Decide what drives the edit

| Material | Primary selection criterion | Appropriate agent workflow |
|---|---|---|
| Podcast, interview, narrated instructional video | Complete and meaningful spoken ideas, accurate chronology/qualifiers, intelligible joins | Transcript/EDL first; then relevant supporting visuals; inspect every cut |
| Family, personal walk/travel, celebration, event reel | Visually compelling, authentic moments: expressions, action, atmosphere, coherent sequence | Inspect a range of moments in the available footage; choose best shot **within** each relevant segment; build a visual story with audio support |
| Product demonstration, tutorial with important screen actions | Essential visual steps and their order, supported by precise narration | Preserve demonstrative frames; never conceal them with generic B-roll |

For visual-story-led work, build a *shot shortlist* before final assembly. Compare candidate moments by **relevance, visible action, expression, composition/framing, stability, image quality, temporal context and natural sound**. Seek the strongest **part of a clip**, not merely a relevant file. Preserve chronological/geographic truth when meaningful; do not manufacture events through unrelated generated pictures. Make a first cut with named uncertain selections or alternatives when the agent cannot confidently judge the emotional peak. A human should review the rough cut before its creative choices are treated as final, when available. The agent should still complete the requested technical deliverable if safe; it must not claim perceptual review it did not perform.

## 1. Transcript-led mode: plan by meaning, then map to frames

1. Inventory all source video/audio and any usable B-roll; protect the original timeline and export a project backup.
2. Retrieve the transcript. `GetTranscription()` may initially return `None` when no transcript exists. Detect this explicitly; if available, call the installed build's `TranscribeAudio()` workflow and then re-read the transcript. Never interpret `None` as an empty or complete transcript. Preserve language and do not invent recognized words.
3. Select **complete ideas**, not arbitrary text snippets: opening/context, important claims, necessary explanation/example, conclusion. Preserve logical order and qualifiers; avoid changing meaning through omission.
4. Prepare an explicit edit decision list (EDL) with source in/out, spoken first/last words, planned destination positions, duration in frames and reasons for each segment. Calculate the target duration by summing frame lengths; do not estimate by the number of sentences. Maintain the source/timeline timebase conversion documented in [timeline-and-media.md](timeline-and-media.md).
5. Assemble a separate editable timeline; inspect continuity and revise where necessary. Avoid including promotional material or repeating ideas unless the user requested them.

## 2. Respect real word and sentence boundaries

- Word-level transcript marks are **candidates**, not guaranteed phonetic boundaries. `TranscribeAudio()` may misrecognize text or place word edges imperfectly.
- Do **not** routinely add fixed handles such as two frames before and three frames after every selected phrase: in the 2026-11-02 task, that captured unwanted words or unrelated footage at multiple cuts.
- Where audio actually has a pause, choose the edit inside the pause; keep only enough breathing space to preserve natural cadence. Where there is no pause, inspect the consonant/breath and image before choosing in/out points. **In improvised, irregular or low-quality speech, automated transcript timestamps alone are not a reliable final cut guide.**
- Joining prepared clips without changing their lengths reduces one class of timing mistakes but **does not** make every audio/video join naturally seamless.

## 3. Optional silence-first workflow

**Use only where the recording contains genuine detectable gaps** between speech and where the user wants pauses reduced.

- DaVinci Resolve's `Ripple Delete Silence` / `Remove Silence` tools can identify low-level sections and provide adjustable pre/post reserves in frames (often exposed as *Pre Head* / *Post Tail*). Review actual UI controls in the installed Resolve build; the API is now declared, but current correctness tests failed. See [21.2 restrictions](resolve-21.2.md#rippledeletesilence-documented-not-approved-by-these-tests) before considering it.
- Before use, protect the original and choose the correct audio source. Tune the threshold, minimum gap and pre/post reserves to the material rather than using a universal preset. Preview short runs first.
- Treat the resulting segments as **candidate source intervals** for content selection. Retain their exact boundaries when possible instead of trimming blindly again.
- Avoid the method when music, room noise, simultaneous speakers, dense speech, sound effects or low-level consonants mean that silence detection is unreliable. It may remove meaningful pauses or quiet syllables.
- After reassembly, listen near every cut; silence removal is not semantic editing or audio quality assurance.

## 4. Conceal a visible picture jump with B-roll — only when safe

**Mandatory gating rule: cover a source picture with B-roll ONLY when the picture being covered is NOT essential to the video's content or the viewer's understanding.** The audible content alone is not sufficient evidence that the on-screen picture is dispensable.

- Appropriate: an ordinary talking head with a distracting jump cut, visually redundant podcast angle or a nonessential background shot. Prefer a B-roll image that supports what is being said. **In personal/event footage, faces, gestures or the original scenery may carry the story even when the words do not refer to them; do not hide those moments.**
- **Do not cover** demonstrations, on-screen controls or software actions, a graph/table, subtitles or labels necessary to understand the explanation, products/details being examined, meaningful gestures, or evidence the viewer is supposed to see. If unsure, preserve the original image or flag for human review.
- Source preference: (1) relevant project B-roll/video, (2) suitable neutral/relevant frames from the source recording, (3) project photographs with restrained motion if appropriate, (4) generated supplemental visuals **only if a generation capability is actually available**, user permissions allow it and the result does not misrepresent events/products/people.
- Put B-roll on a higher video track for only the necessary interval; leave the original **speech audio continuous and independently editable**. Cover both sides of a jump cut when appropriate; check that the overlay enters/exits naturally and does not introduce another abrupt visual mismatch.
- B-roll is a **visual concealment tool**, not a fix for a broken sentence or clipped audio. Do not insert it at every cut. If the shot is essential, repair the edit itself rather than hiding it.

## 5. Judge audio joins separately

- Check whether the first and last syllable of both sides remain complete, background noise changes abruptly, breaths are cut, music changes phase, or a crossfade affects intelligibility.
- Audio waveform continuity, sample discontinuity checks and loudness measurements can prioritize suspicious transitions, but none replace listening. When API access to fades is uncertain, do not invent a method; use available native Resolve controls or flag the transition for the human editor.
- Record each join as `verified by playback`, `technical checks only`, or `needs human listening`. Do not report automatic signal analysis as proof that the entire soundtrack sounds natural. If the recording itself is poor or speech highly irregular, **flag doubtful joins for a human editor** rather than manufacturing a falsely precise automatic result.

## 6. Verify every transition before delivery

- For each cut, inspect at least adjacent frames on both sides. Contact sheets help find one-frame foreign inserts, but also check actual playback/motion, subtitles, and audio.
- If B-roll covers a cut, inspect the source join, the overlay's first/last frames and whether any essential information is concealed.
- Export one representative review render and perform [Render and QA](render-and-qa.md) checks. The 2026-11-02 task revealed one-frame unwanted footage near several earlier joins; revised cuts removed those detected inserts.
- Keep an explicit limitations note if human audio listening, full subtitle proofreading or perceptual QA was not performed.

## External research additions (v1.6) — advisory, not a tested cut engine

The paired *semantic span + acoustic pause* model can map transcript phrases to FFmpeg-detected low-level intervals. The sources, limits, reproducible JSON format and non-destructive analysis utility are described in [Audio analysis and edit-plan data](audio-analysis-and-edit-plans.md). This does not imply that Resolve native `Remove Silence` can be invoked by API. Transcript-based recomposition, acoustic boundaries and human listening supply different kinds of evidence.

The `script-to-broll` library-index pattern from [resolve-toolkit](https://github.com/AdamGarceau/resolve-toolkit) is a possible retrieval aid for interviews and podcasts. A catalog hit is not permission to hide visual information that matters; the B-roll gating rule above remains unchanged.
