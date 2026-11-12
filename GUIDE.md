# Resolve Agent 1.9 — agent-first knowledge base

**Updated:** 2026-11-12 · **Latest recorded Resolve integration environment:** DaVinci Resolve Studio **21.2.0.5**, Windows, Python 3.13.

## Purpose

This is a **searchable reference library**, not a mandatory editing workflow. It helps AI editing agents find existing DaVinci Resolve methods, reusable tools, known failure modes and real-world test evidence *before* spending time rediscovering them. The user's task determines the goals, artistic choices, deliverables and permitted operations. Advertising/editorial techniques are options, not creative requirements.

The public GitHub repository uses **`main` for reviewed knowledge**. Its content may still have version-specific limitations; a merged entry means its evidence was reviewed, **not** that it works everywhere. New discoveries are proposed on separate branches via **Pull Requests (PRs)**. A separate validation agent/reviewer, acting under the repository owner's direction, checks results and approves or rejects the PR. **Editing agents must not write directly to `main` or merge their own proposals.** See [AGENTS.md](AGENTS.md) and [CONTRIBUTING.md](CONTRIBUTING.md).

## Use the library for any task

1. **Identify needs.** Translate the user's brief into required capabilities, not an arbitrary prescribed editing process.
2. **Find a candidate.** Search the [capability index](modules/INDEX.md) (need → solution → relevant traps); follow only the links relevant to this task. If no good method exists, devise an alternative using available tools/documentation.
3. **Check the risks.** Before executing the chosen operation, inspect the relevant entries in [known traps](modules/known-traps.md), version notes and evidence. Absence of a warning **does not** establish safety.
4. **Execute and verify.** Protect original projects and media; test destructive or uncertain operations on a copy when appropriate. Verify actual results and persistence. Distinguish timeline structure, still frames, motion, listening and re-open checks; mark untested aspects as **not checked**.
5. **Capture learning.** Record what worked, failed or remains uncertain, including exact conditions, Resolve build, actions, observed outputs and validation coverage. If new reusable knowledge was found, follow the [contribution protocol](CONTRIBUTING.md) and open a PR **when authorized and when Git/GitHub access is available**. Otherwise include a PR-ready finding in the final task report. **Do not modify the approved library just to record an ordinary task result.**

If a technique fails, check the warnings again, change strategy if useful, and preserve the evidence. A failed but reproducible operation can be as valuable as a working recipe. Never describe a proposal as verified merely because an API call succeeded or an automated check passed.

## Find a method by need

| Need | Solution / starting point | Check before use |
|---|---|---|
| Create, trim or rearrange timeline items | [Timeline and media](modules/timeline-and-media.md), [AV pairing](modules/av-sync-and-trim.md) | [Frame mapping, linking and ripple traps](modules/known-traps.md) |
| Edit speech and use transcript timing | [Transcript-led editing](modules/transcript-driven-editing.md) | [Inaccurate word boundaries and B-roll coverage](modules/known-traps.md) |
| Detect silence or prepare edit intervals | [Audio analysis and plans](modules/audio-analysis-and-edit-plans.md), [silence_probe](tools/README.md) | [`RippleDeleteSilence` and false pauses](modules/resolve-21.2.md), [known traps](modules/known-traps.md) |
| Diagnose sound/picture sync or clipped audio starts | [AV sync and trim](modules/av-sync-and-trim.md), [audio and color](modules/audio-and-color.md) | [Sync assumptions](modules/known-traps.md) |
| Generate titles, animations, Fusion or Word Highlight | [Text+](modules/native-text-plus.md), [Fusion](modules/fusion-and-animation.md), [Word Highlight](modules/word-highlight.md) | [Fusion/DRT traps](modules/known-traps.md) |
| Apply masks, composites or depth-based treatments | [Masking and depth](modules/masking-and-depth.md) | [Matte and Magic Mask limitations](modules/known-traps.md) |
| Make a promotional video more engaging | [Audience engagement](modules/audience-engagement.md), [editing standards](modules/editing-standards.md) | Client's creative brief; [editorial traps](modules/known-traps.md) |
| Assess edits, export frames, compare revisions | [Inspection tools](tools/README.md), [render and QA](modules/render-and-qa.md) | [Quality-check workflow](workflows/quality-check.md) |
| Use current APIs or resolve version conflicts | [Resolve 21.2 reference](modules/resolve-21.2.md) | [Recorded build-specific trials](evidence/resolve-21.2.0.5.md) |
| Look for a method not listed above | [Complete capability index](modules/INDEX.md) | [Known traps](modules/known-traps.md) and [evidence status](modules/evidence-and-research.md) |

## Evidence status and safe decisions

- **Locally tested:** observed working under the stated conditions; test again if material conditions differ.
- **Externally documented:** supported by documentation or external example, not proof of local success.
- **Experimental:** a plausible candidate; a practical trial is still required.
- **Observed to fail:** the operation or assumption failed in a named context; check whether an alternative has been verified.
- **Unverified report:** field observation awaiting independent review; submit via PR, **do not treat as established knowledge**.

Known current caveats: prefer current `GetProperties`/`SetProperties` and `GetSettings`/`SetSettings` forms; native `ExportThumbnails` can review stills but not motion/audio; some video fades did not persist on reopen in recorded 21.2 testing; native `RippleDeleteSilence` failed correctness tests on the recorded material. Do not generalize these observations to other Resolve builds without evidence.

## Contribution and validation loop

**Editing agent → task result and evidence → branch + PR → separately instructed validation agent → approve and merge, or request changes/reject.**

- A proposal should provide a reproducible concise recipe or **action → failure → safer alternative** entry, with source conditions, actual observed result, version and test evidence.
- The proposer may include successful methods, confirmed-looking failures or unresolved observations. Clearly distinguish these; the proposing agent **does not** self-certify a new claim as independently verified.
- A validation agent checks the PR in a separate suitable Resolve environment, records the degree of reproduction, and updates or requests changes. **Only the authorized reviewer/owner merges to `main`.**
- If the agent cannot write files or create a PR, return the proposal text and evidence in its final report. GitHub access is optional for reading this library.
- Never commit proprietary client media, credentials, confidential project data or arbitrary rendered assets to this **public** repository. Use anonymized/minimal evidence; seek approval before publishing sample media.

Detailed instructions: [AGENTS.md](AGENTS.md) · [CONTRIBUTING.md](CONTRIBUTING.md) · [PR template](.github/PULL_REQUEST_TEMPLATE.md).

## Existing tools and workflows

The [optional editing workflow](workflows/editing.md) is an example, **not** an obligatory task sequence. [QA guidance](workflows/quality-check.md) and [the tool catalog](tools/README.md) explain evidence collection. Existing tools are read-only toward Resolve unless a specific tool documents otherwise; they may write local evidence to new paths. The package requires no external model downloads or MCP installation. See the [changelog](CHANGELOG.md) and [historical integration evidence](evidence/resolve-21.2.0.5.md).
