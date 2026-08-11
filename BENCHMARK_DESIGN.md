# FirstRing benchmark design

Date: 2026-08-05

Status: design only. No dataset download, audio capture, model inference, provider call, synthesis, native-speaker review or phone-network experiment was performed in this slice.

## Questions closed by external evidence

| Question | Closed decision |
| --- | --- |
| Do current tests prove speech quality or audio latency? | no; LiveKit tests and FirstRing's simulators are text/timing controls |
| Can one generic multilingual profile represent English and Lithuanian? | no; freeze separate language arms and treat code-switching separately |
| Does Nova-3 provide Lithuanian turn detection? | no; it supports LT transcription, while Flux turn detection omits LT |
| Can FirstRing use the configured LiveKit turn detector for Lithuanian? | no; current audio-model coverage omits LT |
| Can FirstRing use configured Cartesia Sonic for Lithuanian? | no under the published 42-language list |
| Should FirstRing implement ASR, VAD, EOT, TTS or DSP algorithms? | no; maintained components exist; custom work is adapters, receipts and task scoring |
| Is Common Voice or FLEURS sufficient as a production telephone benchmark? | no; both are read speech and published audits warn of dataset quality/transfer issues |
| Should direct speech-to-speech replace the cascade first? | no; preserve transcript/tool/effect observability until a direct-audio arm passes the same task oracle |

## Common evidence contract

Every run records case/audio/derived-audio hashes, dataset revision, speaker partition, language, task category, channel recipe, code/dependency/model/provider/voice pins, prompt/config digest, thresholds, random seed, machine/CPU/GPU, warm/cold state, start/end wall time and external cost. Events use one monotonic clock and retain audio start/end, VAD onset/offset, transcript partial revisions/final, EOT decision, LLM/tool start/end, TTS request/first/last audio, cancellation/resume and final business-effect receipt.

Raw transcripts are immutable. A versioned language-specific normalizer creates a scored copy; WER/CER and entity scores report both raw and normalized variants. Public, project-recorded and synthetic-degradation results remain separate before any pooled summary.

## V0 — real-audio harness and control freeze

Add a test-only PCM/WAV source and event recorder around the existing interfaces. Use a manifest with expected transcript, language, speaker group, task facts and exact booking/CRM/handoff receipt. Preserve all 16 current tests and add mutations that drop/reorder a final transcript, erase a critical entity, mark a clause-internal pause as EOT, fail to cancel audio and issue a wrong/duplicate booking.

PASS requires deterministic replay to produce byte-identical JSON receipts, one monotonic timeline, detection of every mutation and no change to the no-key demo. The harness must accept prerecorded dual-channel fixtures without microphone timing dependence. No model is selected in V0.

Budget: local CPU, one workday, no provider endpoint, no new production dependency.

## V1 — English/Lithuanian ASR by channel

### Data and split

- Mozilla Common Voice 25 Lithuanian and a comparable fixed English subset, sampled speaker-disjoint and never used for threshold tuning after test freeze.
- FLEURS `lt_lt` and `en_us` test/dev partitions for a small parallel read-speech check.
- Project task recordings from at least eight speakers per language, with a minimum of 200 held-out utterances per language and no speaker crossing development/test.
- Task strata: greeting/FAQ, company/person names, Lithuanian diacritics, service names, dates/times, phone numbers, spelled email, corrections, hesitation, code-switch and short acknowledgements.
- Derived conditions: clean 16 kHz; 8 kHz mono G.711 μ-law round trip; background noise at frozen SNRs; room impulse; clipping; and seeded 20/40/80 ms missing spans. Keep one real phone/WebRTC capture set separate from synthetic damage.

Audit at least 10% of public/task labels before scoring and log excluded/corrected cases. Public dataset results cannot substitute for the task set.

### Arms

1. one hosted fixed-language arm: Deepgram Nova-3 `en` and `lt`;
2. one local Whisper arm: Faster-Whisper first, with Whisper.cpp substituted only if its deployment seam wins a short conformance check;
3. NVIDIA Parakeet-TDT 0.6B v3 as the non-Whisper local challenger;
4. optional Azure fixed-language arm only if a second hosted provider is justified;
5. `multi`/automatic language detection as a separate code-switch stress arm, never the monolingual default.

Nemotron 3.5 streaming is not an out-of-box LT arm because LT is adaptation-ready. Admit it only as an explicitly labelled adaptation study after V1 establishes the simpler frontier.

### Metrics and gates

Report raw/normalized WER and CER; exact and token F1 for each critical entity; utterance exact match; partial revision count/stability; speech-end-to-final-transcript p50/p95; real-time factor; peak RAM/VRAM; error/timeout rate; and per-audio-minute provider cost. Bootstrap 95% confidence intervals by speaker, not utterance.

All promoted profiles require zero wrong business effects in the held-out task run and at least 0.98 exact accuracy across the combined phone/date/time/email critical-entity fields. A challenger must reduce normalized error at least 10% relative to the language/channel control or reduce p95 finalization at least 20% without more than a one-percentage-point entity regression. Otherwise keep the simpler/cheaper control. No aggregate bilingual score may hide a failing language or G.711 condition.

## V2 — speech activity and end-of-turn

### Data

Create dual-channel EN and LT conversations with word/pause timings and explicit annotations for speech, clause-internal pause, final turn, abandoned turn, hesitation, self-correction, backchannel and silence/noise. Include at least 150 final turns and 150 non-final candidate pauses per language, speaker-disjoint from tuning. Add the same channel conditions as V1. Use eot-bench's candidate-pause method for English/public comparison and refit its schema for the project Lithuanian set.

### Arms

- VAD: WebRTC aggressiveness sweep; Silero threshold/padding sweep; TEN threshold/hop sweep.
- EOT controls: each VAD plus fixed 250/400/600/900 ms silence.
- English challenger: LiveKit audio turn detector (`v1-mini` local and/or pinned hosted `v1`) with its documented VAD requirements.
- Optional English reference: Smart Turn behind the same adapter.
- Lithuanian: VAD/silence controls only unless a future component explicitly documents LT and passes the admission set.

### Metrics and gates

Frame-level VAD reports precision/recall, false-alarm and miss duration, onset/offset error and RTF. EOT reports false end-of-turn rate at non-final pauses, missed-final rate, decision latency after true speech end, and downstream response latency. Report results by language, pause type and channel.

A promoted EOT profile must have zero clause-internal cutoffs in the critical held-out task subset, at most 2% false EOT and at most 2% missed final turns overall, while improving p95 EOT latency at least 15% against the 600 ms silence control or materially reducing errors at no more than 100 ms p95 latency cost. If no challenger passes, retain fixed silence per language.

## V3 — interruption, false barge-in and overlap

Use dual-channel schedules so the intended user audio starts at known points relative to agent speech. Cover true correction/new request, stop/cancel, short backchannel, cough/throat clear, background speaker, TTS leakage/echo, accidental noise, rapid acknowledgement, and interruption during a tool-bound confirmation. Preserve the exact expected spoken remainder and tool/effect receipt.

Compare eager VAD cancellation; minimum-duration gates; duration plus recognized-word gates; and LiveKit adaptive interruption only when its language/profile coverage is explicitly supported. A later direct-audio arm must run the same cases.

Report true-interruption recall, false-interruption rate, precision, speech-onset-to-duck/cancel p50/p95, unwanted audio after cancel, correct resume rate, duplicated/missing response content and correct final tool/effect rate. Promotion requires at least 0.95 precision and 0.90 recall, p95 cancellation within 350 ms for supported true interruptions, zero false cancellation on the held-out cough/echo subset and zero wrong/duplicate business effects. If adaptive behavior cannot meet the language gate, use local deterministic policies.

## V4 — English/Lithuanian TTS

### Material and arms

Freeze 80 task phrases per language: greeting, FAQ, company/person/service names, Lithuanian diacritics, dates/times, phone digit grouping, spelled email, confirmation/rejection, apology/retry and code-switched proper nouns. Render identical normalized text with:

- Azure Lithuanian voices and one matched English voice;
- Google LT/EN only if provider breadth is justified;
- Cartesia Sonic as English-only;
- Supertonic 3 as the local/private Lithuanian and English control.

Record immutable provider/model/voice ID, text, audio settings, request/first/last audio timestamps, RTF, failures, audio hash and cost. Warm and cold runs are separate.

### Review and gates

At least five native reviewers per language hear blind, randomized, loudness-normalized clips over both headphones and a telephone-band version. They transcribe critical entities and rate intelligibility, pronunciation correctness, naturalness and receptionist appropriateness. Provider identity stays hidden. Report inter-rater agreement, per-category failures and paired bootstrap intervals; automatic MOS predictors may be diagnostics only.

Promotion requires at least 0.98 critical-entity transcription accuracy, no systematic Lithuanian stress/diacritic pronunciation failure identified by a majority of reviewers, and paired preference above 0.50 without a p95 first-audio or cost budget violation fixed before the run. A voice that sounds natural but misreads booking facts fails.

## V5 — complete profile and architecture promotion

Compose only candidates that passed their stage gates. Run at least 100 held-out task conversations per language across clean WebRTC and G.711/noise conditions, with FAQ, qualification, booking conflict, correction, interruption, provider failure and downstream retry cases. Compare a low-latency and high-accuracy cascaded profile; add a direct speech-to-speech arm only if it documents the language, emits a usable shadow transcript, records tool calls and satisfies the same effect oracle.

Report task completion, exact expected tool/effect receipt, unsafe/wrong/duplicate effect rate, unnecessary clarification, abandonment/dead-air, EOT/interruption errors, caller-speech-end-to-first-agent-audio p50/p95, total task duration, provider error, compute/cost and native preference. Promotion requires zero unsafe/wrong/duplicate effects, at least 0.95 task completion, stage gates still passing and reproducible receipts from a clean environment. The selectable toolbox may retain different EN, LT, local-private, low-latency and high-accuracy profiles; a single winner is not required.

## Confounders and stopping rules

- Freeze speaker partitions, source/derived hashes, labels, seeds, normalization, channel recipes, prompts, thresholds, hardware and model/provider pins before the held-out run.
- Never tune on final speakers, final EOT pauses, interruption cases or native review.
- Separate cold start, warmed steady-state, model compute, network/provider time and silence/EOT delay.
- Do not pool read speech, task speech, synthetic damage and real telephone audio into one headline score.
- Do not infer Lithuanian support from “multilingual,” engine availability or English benchmarks.
- Keep VAD, EOT, interruption, ASR, TTS and task-effect failures separately attributable.
- Stop when a simpler language/channel profile passes the paid task; model breadth is not a portfolio objective.
- No client audio, credentials or personal data enter the public evidence bundle without explicit authorization and redaction.
