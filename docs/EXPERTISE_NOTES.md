# FirstRing expertise notes

Date: 2026-08-05

These are research-backed operating rules. Their V-series comparisons have not run.

## Measure a voice profile per language and channel

### Client trigger

- Job wording or deliverable that makes this relevant: bilingual/multilingual receptionist, Lithuanian support, telephony/SIP, low-latency streaming ASR or selectable local/cloud speech.
- How often it appeared in the measured corpus or proposal log: the central portfolio plan identifies EN/LT voice behavior as FirstRing's consequential unproven decision; no frequency claim is made here.
- Existing project/component that can be reused: FirstRing's LiveKit session, deterministic task oracle and booking/CRM/handoff receipts.

### Failure symptom or unanswered choice

A provider or model says “multilingual,” but the system has not shown that a Lithuanian caller on 8 kHz telephone audio can state a name, date, phone number or email without a wrong downstream action.

### Competing options

| Option | Why it is plausible | Main cost or failure risk |
| --- | --- | --- |
| one multilingual default | simplest routing and supports code-switching in theory | aggregate quality can hide a failing language; feature coverage differs by language |
| fixed EN and LT profiles | explicit support and thresholds per language | routing/configuration and two evidence gates |
| local/private plus hosted variants | privacy/cost/resilience choice | more adapters and hardware/provider measurements |

### Controlled comparison

- Evidence-reuse level: triangulated external answer for capability screening; new-data comparison required for local winners.
- External sources and applicability checks: Deepgram documents Nova-3 `lt` but Flux turn detection omits LT; LiveKit's audio turn detector omits LT; Cartesia's current language list omits LT; Azure/Google publish LT voices.
- Contrary evidence, benchmark limitations, or unresolved disagreement: Common Voice and FLEURS are read speech; a 2025 audit reports quality problems in multilingual datasets; provider support does not predict FirstRing task/entity accuracy.
- Representative cases or fixtures: speaker-disjoint EN/LT public speech plus FirstRing names, dates, times, phone, email, corrections and code-switch cases under clean and G.711/noise conditions.
- Frozen development/held-out split, when relevant: speaker-disjoint per language; public, task and real-phone sets remain separate.
- Metrics and decision thresholds chosen before the run: WER/CER, critical-entity exact accuracy, finalization latency, task/effect correctness, cost and compute as V1/V5 define.
- Runtime, hardware, model/provider version, cost assumptions, and date: record per run; research date 2026-08-05.
- What is deliberately outside the comparison: provider production SLA, unseen accents, production concurrency and business uplift.

### Result

External evidence rejects a single current bilingual preset: the configured recognition, EOT and TTS pieces do not share Lithuanian coverage. No FirstRing audio winner exists yet.

### Decision rule

Promote EN and LT independently by channel. Treat automatic/multilingual routing as a separate code-switch arm. Retest only when documented coverage, target hardware/channel or task vocabulary changes.

### Delivery control

Profile selection fails closed when a requested language is unsupported, and every task run retains the requested language, model/voice/config pins and exact business-effect receipt.

### Reuse boundary

- Reusable without client data: language/channel matrix, public fixtures, manifests, receipt schema and promotion logic.
- Requires client data, credentials, environment, or acceptance criteria: target speakers, carrier audio, provider cost/latency and business vocabulary.
- Unsupported claim that must not appear in a proposal: FirstRing currently achieves usable English/Lithuanian telephone accuracy or provider-grade latency.

### Proposal-safe insight

I qualify a voice stack per language and channel rather than trusting a “multilingual” label. For booking flows I score names, dates and contact details separately from average transcript error, because those are the errors that create wrong actions.

### Evidence

- Code: current FirstRing at `79a92a4`; planned adapters in `GITHUB_IMPLEMENTATION_AUDIT.md`.
- Tests: current 16 deterministic tests; V0-V5 are unrun.
- Raw comparison artifacts: none yet.
- Human review, if used: V4 design only.
- Reproduction command: to be recorded by the first experiment.

### Interview follow-up

- Likely technical question: Why not just use automatic language detection?
- Short answer: it is useful for routing/code-switching, but it cannot compensate for an EOT or TTS component that lacks Lithuanian coverage, and its errors need their own task-level test.
- Deeper evidence to open if challenged: `TECHNIQUE_TAXONOMY.md`, V1/V5, provider language pages and the critical-entity receipt design.

### Central index disposition

- Added or updated card in `UPWORK_EXPERTISE_INDEX.md`: update existing card only.
- Card heading, if indexed: **Measure English and Lithuanian separately**.
- If not indexed, exact reason: this deepens the existing ContextSidecar-derived card with channel, EOT/TTS coverage and effect-receipt rules; a duplicate card would weaken retrieval.

## Separate speech activity, turn completion and interruption policy

### Client trigger

- Job wording or deliverable that makes this relevant: barge-in, natural conversation, endpointing, false interruptions, low response latency or noisy calls.
- How often it appeared in the measured corpus or proposal log: not measured; it is a direct FirstRing acceptance risk.
- Existing project/component that can be reused: LiveKit turn/interruption surfaces, eot-bench, Silero/TEN/WebRTC candidates and the existing simulated interruption scenario.

### Failure symptom or unanswered choice

An agent answers during a caller's pause, waits too long after a finished sentence, or stops speaking because of a cough/backchannel. One “VAD threshold” is incorrectly expected to solve all three behaviors.

### Competing options

| Option | Why it is plausible | Main cost or failure risk |
| --- | --- | --- |
| VAD plus silence | language-agnostic and inspectable | cannot know whether a clause is complete |
| semantic/audio EOT | uses content/acoustic completion cues | language coverage and model/runtime dependency |
| eager/adaptive interruption | faster or more natural barge-in behavior | false cancellations, cloud/language constraints |

### Controlled comparison

- Evidence-reuse level: established external distinction; FirstRing threshold/profile winner requires new-data comparison.
- External sources and applicability checks: LiveKit explicitly layers turn detection on VAD and publishes separate interruption tuning; eot-bench scores every candidate pause.
- Contrary evidence, benchmark limitations, or unresolved disagreement: LiveKit and Smart Turn omit Lithuanian; TEN's published VAD advantage is vendor-benchmarked and is not EOT evidence.
- Representative cases or fixtures: clause pauses, final turns, hesitation, correction, backchannel, cough, background speaker, echo and true stop/new-request overlap in EN/LT.
- Frozen development/held-out split, when relevant: speaker-disjoint pause and overlap cases.
- Metrics and decision thresholds chosen before the run: frame VAD errors; EOT false/missed decisions and latency; interruption precision/recall/cancellation/resume as V2/V3 define.
- Runtime, hardware, model/provider version, cost assumptions, and date: record per profile; research date 2026-08-05.
- What is deliberately outside the comparison: production carrier AEC behavior and unsupported-language semantic models.

### Result

External evidence closes the decomposition and the Lithuanian coverage boundary. The best FirstRing thresholds/components remain unknown.

### Decision rule

Tune VAD for speech presence, EOT for reply timing and interruption for cancellation intent. Use semantic/audio EOT only for explicitly supported languages; retain a measured silence fallback per language/channel.

### Delivery control

Emit distinct event types and reports for VAD, EOT and interruption. A profile cannot promote by improving latency if it introduces clause cutoffs, false cancellation or a wrong tool effect.

### Reuse boundary

- Reusable without client data: event schema, eot-bench refit, behavior categories and gates.
- Requires client data, credentials, environment, or acceptance criteria: caller pause style, acoustic echo/noise and acceptable response/cancel latency.
- Unsupported claim that must not appear in a proposal: semantic Lithuanian EOT or adaptive-interruption performance is already supported/proven.

### Proposal-safe insight

I test speech detection, end-of-turn timing and interruption intent separately. That prevents a low-latency setting from looking good while it cuts off callers or treats a cough as a new instruction.

### Evidence

- Code: planned seams in `GITHUB_IMPLEMENTATION_AUDIT.md`.
- Tests: V2/V3 design only.
- Raw comparison artifacts: none yet.
- Human review, if used: annotation adjudication planned for ambiguous turn/interrupt labels.
- Reproduction command: to be recorded by the first experiment.

### Interview follow-up

- Likely technical question: Isn't VAD the end-of-turn detector?
- Short answer: VAD says speech versus non-speech; EOT decides whether a silence completes the user's turn; interruption policy decides whether new activity should cancel the agent.
- Deeper evidence to open if challenged: V2/V3, LiveKit turn docs, eot-bench and the language support matrix.

### Central index disposition

- Added or updated card in `UPWORK_EXPERTISE_INDEX.md`: add distinct card.
- Card heading, if indexed: **Separate speech activity, turn completion and interruption policy**.

## Keep a cascaded voice path when tool evidence matters

### Client trigger

- Job wording or deliverable that makes this relevant: voice agent with booking, CRM, qualification, compliance/audit trail, tool calling or deterministic handoff.
- How often it appeared in the measured corpus or proposal log: not measured; FirstRing directly combines voice with booking and CRM effects.
- Existing project/component that can be reused: cascaded LiveKit pipeline and the booking/CRM/DeliveryGuard receipt path.

### Failure symptom or unanswered choice

A direct speech-to-speech model sounds fluid, but the team cannot show what it heard, which facts drove a tool call, or why the final CRM/booking effect was correct.

### Competing options

| Option | Why it is plausible | Main cost or failure risk |
| --- | --- | --- |
| cascaded STT-LLM-TTS | replaceable stages and inspectable transcript/tool/spoken text | accumulated latency and error propagation |
| direct half/full-duplex audio model | natural timing and prosody; simultaneous listening/speaking | language/task evidence and intermediate observability may be weak |
| hybrid direct audio plus shadow evidence | preserves richer interaction while recording a parallel trace | added cost, synchronization and disagreement handling |

### Controlled comparison

- Evidence-reuse level: triangulated architecture decision; local end-to-end comparison required before changing FirstRing.
- External sources and applicability checks: Moshi/PersonaPlex demonstrate full duplex; Full-Duplex-Bench covers pause/backchannel/interruption; task-grounded 2026 studies show voice task completion remains a distinct failure surface.
- Contrary evidence, benchmark limitations, or unresolved disagreement: naturalness can improve even when tool accuracy or transcript auditability does not; open-model Lithuanian task support is unestablished.
- Representative cases or fixtures: held-out qualification, FAQ, booking conflict, correction, interruption and failure/retry conversations with exact effects.
- Frozen development/held-out split, when relevant: V5 profiles use identical dual-channel cases and expected receipts.
- Metrics and decision thresholds chosen before the run: task completion, exact effect, unsafe/duplicate effect, interruption/EOT, speech-end-to-first-audio, cost and native preference.
- Runtime, hardware, model/provider version, cost assumptions, and date: per V5 run; research date 2026-08-05.
- What is deliberately outside the comparison: open-ended companionship and expressive entertainment where tool evidence is not the paid outcome.

### Result

The cascade is retained as the evidence-bearing default. Direct speech-to-speech is a deferred challenger, not rejected technology.

### Decision rule

Admit direct audio only when it supports the target language, records a usable shadow transcript and tool calls, passes the same business-effect oracle, and materially improves interaction or latency. Otherwise optimize or swap cascade stages.

### Delivery control

Every spoken task links audio/transcript revisions, extracted facts, tool request, tool result, downstream effect and output text/audio hash. Disagreement between direct model behavior and shadow evidence blocks automatic promotion.

### Reuse boundary

- Reusable without client data: architecture admission gate and receipt chain.
- Requires client data, credentials, environment, or acceptance criteria: target language/model, tools, latency budget and acceptable audit trail.
- Unsupported claim that must not appear in a proposal: direct speech-to-speech is inherently safer/faster for FirstRing or has proven LT tool accuracy.

### Proposal-safe insight

For voice workflows that create bookings or CRM updates, I keep a trace from heard text to tool arguments and effects. A direct-audio model is worth testing for fluidity, but it does not replace the task/effect acceptance oracle.

### Evidence

- Code: current cascaded FirstRing and planned V5 receipt schema.
- Tests: deterministic task/effect tests exist; direct-audio comparison is unrun.
- Raw comparison artifacts: none yet.
- Human review, if used: V5 native preference planned.
- Reproduction command: to be recorded by V5.

### Interview follow-up

- Likely technical question: Are cascades obsolete now that realtime speech-to-speech models exist?
- Short answer: not when the paid task needs replaceable providers, exact fact extraction and auditable tool effects; direct audio becomes a challenger under the same oracle.
- Deeper evidence to open if challenged: V5 and the full-duplex evidence matrix.

### Central index disposition

- Added or updated card in `UPWORK_EXPERTISE_INDEX.md`: add distinct card.
- Card heading, if indexed: **Keep a cascaded voice path when tool evidence matters**.

## Judge TTS with native task phrases, not naturalness alone

### Client trigger

- Job wording or deliverable that makes this relevant: Lithuanian voice, customer-facing receptionist, names/dates/numbers, branded terms or low-latency streaming TTS.
- How often it appeared in the measured corpus or proposal log: not measured; explicit bilingual output is a FirstRing requirement.
- Existing project/component that can be reused: FirstRing response text and booking confirmations; Azure/Google/Supertonic candidates.

### Failure symptom or unanswered choice

A voice sounds pleasant in a vendor demo but mispronounces a Lithuanian name, reads a phone number ambiguously, delays the first audio, or becomes unintelligible after telephone-band conversion.

### Competing options

| Option | Why it is plausible | Main cost or failure risk |
| --- | --- | --- |
| vendor sample/model claim | cheap initial screening | curated text and no task/channel evidence |
| automatic quality score | scalable diagnostic | weak proxy for pronunciation and business-fact comprehension |
| blind native task review | directly tests user-visible outcome | reviewer time and careful randomization needed |

### Controlled comparison

- Evidence-reuse level: external capability screening plus new native-speaker comparison.
- External sources and applicability checks: Azure/Google publish Lithuanian voices; Supertonic 3 explicitly lists Lithuanian and provides an ONNX runtime; Cartesia/Piper/MMS currently fail the exact LT artifact screen.
- Contrary evidence, benchmark limitations, or unresolved disagreement: a voice may win naturalness but lose entity intelligibility; Supertonic's LT task quality and target-machine latency are unknown.
- Representative cases or fixtures: greetings, names, diacritics, dates/times, phone groups, spelled email, apologies, confirmations and code-switched proper nouns.
- Frozen development/held-out split, when relevant: blind randomized held-out 80-phrase set per language.
- Metrics and decision thresholds chosen before the run: entity transcription, pronunciation, intelligibility, naturalness, appropriateness, first-audio p95, RTF, errors and cost.
- Runtime, hardware, model/provider version, cost assumptions, and date: per V4 run; research date 2026-08-05.
- What is deliberately outside the comparison: voice cloning, emotion acting, production concurrency and long-form narration.

### Result

Capability screening identifies credible hosted and local LT candidates and rejects the current Cartesia/Piper LT assumptions. No voice-quality winner exists yet.

### Decision rule

Shortlist from documented language coverage, then promote by blind native task review and latency/cost budgets. Critical fact intelligibility is a hard gate; naturalness is a secondary preference.

### Delivery control

Store normalized request text, immutable voice/model ID, audio hash and telephone-band derivative; reviewers transcribe critical facts without seeing provider identity.

### Reuse boundary

- Reusable without client data: generic task phrase categories, blind package and scoring form.
- Requires client data, credentials, environment, or acceptance criteria: brand/proper names, target carrier, native reviewers and cost/latency budget.
- Unsupported claim that must not appear in a proposal: any candidate is already the best or most natural Lithuanian voice for FirstRing.

### Proposal-safe insight

I shortlist TTS by documented language support, then test it on the names, dates and contact details callers actually need to understand. Naturalness cannot compensate for a misread booking fact.

### Evidence

- Code: V4 package design in `BENCHMARK_DESIGN.md`.
- Tests: unrun.
- Raw comparison artifacts: none yet.
- Human review, if used: five native reviewers per language planned; no review performed.
- Reproduction command: to be recorded by V4.

### Interview follow-up

- Likely technical question: Why not use an automatic MOS model?
- Short answer: it can flag broad quality, but it does not prove that native callers understand a Lithuanian name, date, number or code-switched term over the target channel.
- Deeper evidence to open if challenged: V4, the provider coverage sources and review gates.

### Central index disposition

- Added or updated card in `UPWORK_EXPERTISE_INDEX.md`: add distinct card.
- Card heading, if indexed: **Judge TTS with native task phrases, not naturalness alone**.
