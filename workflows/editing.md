# Editing workflow

> [Start page](../GUIDE.md) · [Completion checks](quality-check.md) · [Current API](../modules/resolve-21.2.md)

## Start here: the shortest useful workflow

**Default:** preserve the source, choose a meaningful moment, keep its original picture and sound relationship, make a simple cut, and check the result. Add a technique only when it solves an observed problem or serves the brief.

| Step | Do this | Ready to continue when… |
|---|---|---|
| 1. Understand and protect | Record the requested result, editing mode, deliverables and constraints in a few lines. Read the live project/timeline IDs, media paths, FPS and tracks. Save a backup and use a clearly named working duplicate for a new montage or experiment. | The intended target is unambiguous, media is available, and the original can be recovered. Reuse the identified working copy on reruns. |
| 2. Check review access | Try a short representative passage containing speech and visible action. Establish whether the reviewer can actually receive moving video and audio. | Record separately: frame inspection, motion review and listening available/unavailable, with the tool or reviewer. A running player or moving audio meter is insufficient. |
| 3. Select content | Survey all relevant sources, then inspect promising intervals more closely. Note source, in/out candidates and one sentence explaining why each moment belongs. | Each choice contributes context, action, reaction, information or a result. Important speech/action has a beginning and an ending. |
| 4. Prove one operation | In the working/test copy, try one representative insertion and cut with the actual source/timeline FPS. If needed, test linked trim, move and transition. Read back and inspect the result; check persistence of newly used effects. | You know what changed, which units were used and how to verify it. Failed or uncertain experiments are resolved before batch editing. |
| 5. Assemble and refine | Build native editable clips. Keep original AV pairs together unless the brief calls for a deliberate split. Review a short section before repeating the technique. Update actual state after every editing pass. | The story is understandable; no accidental gaps, unlinked edits or unwanted source fragments have been introduced. |
| 6. Check and deliver | Review every join in context, then the whole edit with picture and sound. Save/reopen and compare relevant state. Produce only the requested deliverables, with media paths and unresolved review locations. | Checks below are complete, or the result is explicitly identified as a draft with exact remaining checks. |

**Choose the mode once:** speech-led → preserve complete ideas and qualifiers; event/travel/family → preserve meaningful actions, faces and reactions; tutorial → preserve every necessary visual step. Mixed material can use different modes per scene. Do not impose a runtime or equal shot lengths when none was requested.

Test a new operation/source-rate combination once, then reuse the verified method. Repeat a test only after a relevant change, failure or unexplained result. Fix the observed issue and return to editing; unrelated API research is optional.

**Read by need:** ordinary montage → this page, [timeline operations](../modules/timeline-and-media.md), [AV pairing](../modules/av-sync-and-trim.md), [QA](../modules/render-and-qa.md). Open transcript, titles, Fusion or masking modules only when the task requires them. Experienced agents can go directly to the topic index after checking the live target and review capabilities.

## A repeatable recipe for a good cut

1. **Choose the moment first.** Keep enough setup to understand the action, its payoff and the useful reaction. For speech, preserve the whole intended thought. Compare nearby source alternatives before accepting an awkward boundary.
2. **Check both sides in context.** Start playback a few seconds before the proposed join and continue a few seconds after; extend to the complete sentence/action as needed. Inspect adjacent frames too. Sparse contact sheets locate candidates; they do not establish exact cut points.
3. **Make the smallest effective edit.** Start with a straight picture cut and original linked sound. Trim/move both members of an ordinary AV pair together. For intentional J/L cuts, retain the source-time relationship in the overlap and record the split; unequal edges alone are then expected.
4. **Listen before adding a transition.** If a join clicks or ambience changes distractingly, adjust the boundary or test a short native audio fade/crossfade using sufficient source handles. Listen again: a crossfade can overlap words, double an impact or change the level. Its duration and curve are choices, not a universal preset.
5. **Check the actual result.** Confirm source identity, picture/audio placement and the first/last audible syllable or meaningful action. If still uncertain, keep a more complete passage and mark the exact join for review. Do not keep tightening from waveform valleys or unreliable word timings alone.

Example: for a child helping to weigh flour, retain enough to see the action and the child's response. End after the useful outcome, before an irrelevant camera turn, if speech allows. There is no need to derive the shot length from a transcript or a target number of seconds.

## When something is uncertain

| Observation | Next action | Evidence needed to close it |
|---|---|---|
| Frames are available, but motion/audio is not | Use a supported audiovisual review tool or reviewer if available. If not, finish safe technical work as a revisable draft; retain wider uncertain boundaries and list exact review times. | Actual playback/listening of named intervals. Exporting a WAV or opening a player alone does not count. |
| Transcript repeats, invents words or mismatches speech | Before a full batch, test a short clear passage and a difficult one in the actual language. Reject unreliable text/timing for precise cuts; use content review and wider passages. | First/last words and their timing checked against the audio by a capable reviewer. Without listening, transcription suitability remains unverified. |
| Quiet start/end in a source | Measure that file's edges and channels; inspect stream start times. Distinguish low signal, missing sound and an AV offset. Preserve AV alignment when excluding a defective passage. | File-specific measurements and playback of the same event. Never shift audio by a blanket 0.3 s correction. |
| Suspected sound/picture mismatch | Compare the same visible/audible event in the source, an untouched Resolve pair and the edited pair. Follow [AV diagnosis](../modules/av-sync-and-trim.md). | A localized, repeatable offset with units and reference event; neither FPS differences nor linkage alone diagnose it. |
| API returns success but output is wrong or disappears | Read actual values, inspect output, save/reopen the protected working project and check again. Use a tested native alternative if necessary. | Persisted state **and** visible/audible result. Do not repeat the same ineffective call across the montage. |
| Script or API signature is uncertain | Check the installed `.pyi`/README and run one bounded test. On unexpected read-back, stop that batch and inspect the affected items before retrying. | Supported signature and correct actual change, including linked items. Avoid method-name guessing or blind reruns. |
| Measurements flag a large level change | Listen around the join and compare similar content. Change gain only when the difference is unwanted. | Perceptual improvement and acceptable resulting peaks. A pause followed by speech is not automatically a defect. |

Run one heavy transcription/model job at a time when resources are shared with Resolve. A failed pilot is a reason to change the method, not automatically to download a larger model. Cache useful analysis; preserve time for actual content review.

## Keep one current record, with simple units

For a small edit, a short table and a current Resolve read-back are enough. For automation, use a structured manifest. **Plan and actual state are separate fields or files:** after a trim, move or transition change, refresh actual state and invalidate affected QA. Never use an earlier plan as proof of the finished timeline.

Record only what is needed to resume and verify: project/timeline IDs, revision or capture time, source identity/path, intended and actual ranges, reason for selection, original AV relationship, changed gain/fades/transitions, and review status. A selection note such as “complete closing thought” is an intention until checked; recheck it after a trim. Bind each QA render/report to that revision; record the render time/path and settings. A later unchanged duration does not prove an older WAV still represents the current mix.

| Value | Record explicitly |
|---|---|
| Source range | Source frames or source seconds; identify which and whether the out point is exclusive. Do not mix requested and returned ranges. |
| Timeline range | Absolute frames plus timeline start frame; display review locations also as elapsed time from the start. |
| FPS | Rational rate where established, e.g. `30000/1001`; keep Resolve's displayed FPS separately. Do not silently substitute `30/1` or infer variable-frame-rate timing from one average. |
| Handles / offsets | Name the API getter and its verified timebase. Available extension is not automatically a source frame index. |
| Timecode | Distinguish timecode labels from elapsed seconds and record drop-frame/non-drop-frame mode. Do not generalize a nominal-30 timecode helper to other projects. |
| Test result | Actual expected/observed values and units, tolerance, coverage and evidence path. Use `not_checked` when no check ran, never a hard-coded success flag. |

See [data-contract examples](../modules/audio-analysis-and-edit-plans.md) for larger automated edits. These are library conventions, not native Resolve import formats.

