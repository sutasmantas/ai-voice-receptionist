# FirstRing GitHub implementation audit

Date: 2026-08-05

Status: component-level, GitHub-first audit. Repository health is a dated implementation signal, not a popularity contest.

## Current composition and boundary

FirstRing began from the official `livekit-examples/agent-starter-python` template and retains `src/agent.py` as the LiveKit entry point. It already refits:

- LiveKit's no-key fake-LLM/testing pattern;
- LeadDock's booking/CRM boundary;
- a hash-checked vendored DeliveryGuard wheel for durable handoff behavior;
- RapidFuzz for closed-world FAQ retrieval.

At base `79a92a46971f3ecb8a5ba2e596a2e8b2b92f97a0`, the optional hosted profile selects Deepgram Nova-3 with `language="multi"`, Cartesia Sonic-3, `inference.TurnDetector()`, ai-coustics enhancement and preemptive generation. The deterministic profile passes text through `DeterministicStt`, emits duration chunks from `DeterministicTts`, fixes response latency at 120 ms and simulates interruption from known timestamps. Those components are useful controls, but they never ingest or emit audio.

The consequential custom seams are therefore not model internals. They are: audio-case manifests, adapter-normalized events, language/channel configuration, transcript revision receipts, entity/task scorers, turn/interruption labels, TTS review packages and end-to-end promotion rules.

## Dated repository audit

Exact default-branch commits were read through the GitHub API on 2026-08-05. Open-issue counts are triage context only; they do not select a winner.

| Repository | Exact pin | Last push observed | Health/use decision |
| --- | --- | --- | --- |
| [livekit/agents](https://github.com/livekit/agents) | `04d00cbd311fa980f5276b7eb29aa099f2ea16ff` | 2026-08-05 | active; retain existing framework rather than migrate |
| [livekit/eot-bench](https://github.com/livekit/eot-bench) | `0c6c86768921bb44eee64f9b9b3427689dceeeaa` | 2026-06-17 | active small benchmark; adopt/refit pause-scoring harness |
| [pipecat-ai/pipecat](https://github.com/pipecat-ai/pipecat) | `0db3c9a0a8d4982c997afd073a3f6372e9d44515` | 2026-08-04 | active alternative framework; do not introduce a second orchestration stack |
| [pipecat-ai/smart-turn](https://github.com/pipecat-ai/smart-turn) | `4786657e242dfe77dd138699ac564ee074a2a543` | 2026-01-29 | maintained EN-capable EOT reference; LT absent |
| [snakers4/silero-vad](https://github.com/snakers4/silero-vad) | `76e3dc408eb2a5c655c34e230d2d5459b4439daa` | 2026-07-16 | active; first neural VAD candidate and existing LiveKit seam |
| [TEN-framework/ten-vad](https://github.com/TEN-framework/ten-vad) | `22a3bcd4509d0faaa8eef4881e8af5f39c178950` | 2026-02-02 | maintained; challenger with open test set, not presumed winner |
| [daanzu/py-webrtcvad-wheels](https://github.com/daanzu/py-webrtcvad-wheels) | `ad6c22d895f7f4a44706a72a8a4ddd53e78f80fe` | 2026-01-12 | maintained binary-wheel fork; frame-level control |
| [wiseman/py-webrtcvad](https://github.com/wiseman/py-webrtcvad) | `e283ca41df3a84b0e87fb1f5cb9b21580a286b09` | 2024-07-04 | older wrapper; superseded for the experiment by maintained wheels |
| [openai/whisper](https://github.com/openai/whisper) | `5f86d1d86363843179951550570367b37c5d6f78` | 2026-07-28 | active reference implementation/model family; do not duplicate decoder logic |
| [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper) | `ed9a06cd89a93e47838f564998a6c09b655d7f43` | 2025-11-19 | maintained CTranslate2 runtime; preferred Python local Whisper seam |
| [ggml-org/whisper.cpp](https://github.com/ggml-org/whisper.cpp) | `306c88f4d1286aec1bf96e544632897886af5501` | 2026-08-04 | highly active portable/quantized runtime; process/server alternative |
| [NVIDIA-NeMo/NeMo](https://github.com/NVIDIA-NeMo/NeMo) | `40ace43c7cf151af78dc22027c02feeca7e06b6a` | 2026-08-05 | active but heavy; reuse Parakeet/Nemotron inference, never reimplement transducers |
| [k2-fsa/sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) | `00ad9a19a63751a6c4b12050a00eacfeb204814e` | 2026-08-04 | active cross-platform ASR/TTS/VAD runtime; reference if ONNX deployment becomes a real constraint |
| [supertone-inc/supertonic](https://github.com/supertone-inc/supertonic) | `7e2804f96016a7028cb1ed627353c61c1e9dd281` | 2026-07-24 | active ONNX/on-device TTS; explicit LT support makes it the local V4 candidate |
| [facebookresearch/fairseq](https://github.com/facebookresearch/fairseq) | `3d262bb25690e4eb2e7d3c1309b1e9c406ca4b99` | 2025-09-30 | archived; MMS exact TTS list omits LT, so reject as an LT control |
| [OHF-Voice/piper1-gpl](https://github.com/OHF-Voice/piper1-gpl) | `ffb62233b04dd0b04f005cd7c1f879eb9b0889fd` | 2026-08-04 | active engine; reject LT today because official voice index has no LT voice |
| [iver56/audiomentations](https://github.com/iver56/audiomentations) | `f5e45049dfa8b33e8ee79a900b2b796a9dcae45f` | 2026-04-13 | active; adopt frozen noise/impulse/clipping/gap transforms |
| [FFmpeg/FFmpeg](https://github.com/FFmpeg/FFmpeg) | `d295add2225e1ad9ba9d55cb612cce50072dc45d` | 2026-08-05 | active; adopt G.711/resampling CLI recipes instead of custom codec/DSP code |
| [kyutai-labs/moshi](https://github.com/kyutai-labs/moshi) | `e6a55d2722a65870ef52a6c9f6ecfc0e90f38362` | 2026-05-16 | maintained full-duplex research implementation; defer integration |
| [NVIDIA/personaplex](https://github.com/NVIDIA/personaplex) | `3428dfd95309a7f3c84fd93259ded0f810d1ff91` | 2026-03-02 | maintained Moshi-derived persona/full-duplex implementation; defer integration |

## Component decisions by seam

### Audio case and channel preparation

**Adopt:** audiomentations for deterministic additive/background noise, impulse responses, clipping, gain and missing spans; FFmpeg for 8 kHz mono G.711 μ-law/A-law round trips and resampling.

**Project-owned thin code:** one manifest loader that hashes source audio and recipe parameters, creates immutable derived-case IDs and records tool versions. It must not implement filters, codecs or resamplers.

**Why:** channel corruption is supporting test machinery, not FirstRing's differentiating logic. Mature DSP tooling is cheaper to validate and easier to reproduce.

### ASR adapter

**Adopt:** existing LiveKit provider interfaces for hosted ASR; one local Whisper implementation (Faster-Whisper first if in-process Python remains acceptable, otherwise Whisper.cpp behind a process); NeMo only for the distinct Parakeet/Nemotron arms.

**Project-owned thin code:** normalize partial/final transcript events into `{case_id, profile_id, language_requested, language_detected, text, words, event_time, is_final, model_pin}`. The harness owns text normalization and task-entity scoring, not decoding.

**Avoid:** wrapping several Whisper runtimes into permanent production dependencies merely to create breadth. Compare deployment seams once, then run one representative Whisper arm.

### VAD and end-of-turn adapter

**Adopt:** maintained WebRTC wheels, Silero and TEN behind a common frame-probability/activity interface. Refit eot-bench's candidate-pause method and receipts. Use LiveKit's audio turn detector only for supported languages.

**Project-owned thin code:** translate detector outputs to common candidate-pause decisions and join them to annotated turn boundaries. Keep VAD speech labels separate from EOT predictions.

**Avoid:** a custom energy/VAD model, copying model internals, or treating Smart Turn/LiveKit English coverage as Lithuanian support.

### Interruption and duplex adapter

**Adopt:** LiveKit's existing cancellation/resume primitives and configurable duration/word/adaptive policies. Reuse Full-Duplex-Bench categories for pause, backchannel, smooth turn, interruption and overlap coverage.

**Project-owned thin code:** dual-channel fixture schedule, event recorder, intended-interruption labels, cancellation latency and resume/correct-tool-effect oracle.

**Avoid:** migrating to Pipecat to gain Smart Turn, or embedding Moshi/PersonaPlex before FirstRing can retain shadow transcripts and tool/effect receipts. Framework migration would expand integration surface without solving Lithuanian coverage.

### TTS adapter and review package

**Adopt:** provider adapters for Azure/Google/Cartesia arms; Supertonic 3 through its ONNX/Python/server seam for the local LT control. Store exact voice/model identifiers.

**Project-owned thin code:** capture request text, normalized spoken form, first/last audio timestamps, audio hash, sample rate/codec and blind randomized review IDs. Reviewers score task phrases; they do not need provider names.

**Avoid:** training a Lithuanian voice, writing a TTS engine, or adopting Piper/MMS merely because the engine/family advertises broad coverage. A missing exact language artifact is a capability gap, not an integration task.

### Task and effect oracle

**Retain/refit:** FirstRing's existing qualification, FAQ, booking, CRM and DeliveryGuard contracts. The audio harness should feed final/partial transcripts into the same task path and compare tool arguments/effects to a frozen expected receipt.

**Project-owned thin code:** critical-entity alignment for name, company, date, time, phone, email and requested service; task success; invalid-effect mutation checks. This is the portfolio-specific value and cannot be copied from a generic ASR benchmark.

## Adopt / refit / custom / reject summary

| Disposition | Scope |
| --- | --- |
| adopt | LiveKit session/provider contracts; one Whisper runtime; Parakeet/Nemotron inference; WebRTC/Silero/TEN; FFmpeg; audiomentations; Supertonic 3 |
| refit | eot-bench candidate-pause harness; Full-Duplex-Bench behavior categories; existing FirstRing booking/CRM/handoff oracle |
| custom thin glue | manifests/hashes; event schema; language/channel profiles; transcript normalization; entity/task metrics; native-review package; promotion receipt |
| reject now | new speech/VAD/DSP algorithms; Pipecat framework migration; Smart Turn for LT; Cartesia/Piper for LT; direct speech-to-speech as first depth implementation |

## Minimal integration checks

1. Preserve the current deterministic session, API, UI and workflow tests with no provider credentials.
2. Every audio run records source and derived hashes, recipe, sample rate/codec, code/dependency/model pins, language route, hardware and warm/cold status.
3. Adapter conformance tests replay one fake partial/final/cancel/error stream per provider/runtime without network access.
4. Transcript scoring retains raw and normalized hypotheses; normalization rules are versioned and cannot erase entity errors.
5. VAD, EOT and interruption have different event types and metrics; a passing VAD result cannot satisfy an EOT or barge-in gate.
6. Unsupported-language configurations fail closed at startup or profile selection; `multi` never overrides a documented coverage gap.
7. TTS review packages are blind and include critical names, Lithuanian diacritics, dates, times, phone numbers, email spelling and code-switched phrases.
8. Tool/effect receipts prove that a spoken case caused exactly the expected booking/CRM/handoff state; audio quality alone cannot promote a profile.
9. All optional candidates remain removable while the no-key deterministic demo stays usable.
