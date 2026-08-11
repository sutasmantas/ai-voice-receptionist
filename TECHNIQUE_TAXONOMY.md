# FirstRing technique taxonomy

Date: 2026-08-05

Status: systematic research dossier. No audio/model/provider experiment or implementation is authorized in this slice. Conclusions use `established`, `provisional`, `contested`, or `unknown`.

## Decision boundary

FirstRing currently proves a bounded receptionist workflow: a LiveKit `AgentSession`, streaming STT/LLM/TTS interfaces, transcript events, interruption handling, FAQ grounding, qualification, booking, CRM upsert and a DeliveryGuard-backed downstream handoff. Its no-key profile and 16-test suite are deterministic text/timing simulations. They do not feed audio into an ASR model, synthesize audible speech, traverse a telephone network, measure end-of-turn decisions, call a hosted model, or establish English or Lithuanian speech quality.

The paid outcome is not “a voice model.” It is a caller completing a receptionist task without being misheard, cut off, trapped in silence, given an unintelligible response, or causing the wrong booking/CRM effect. Speech activity, turn completion, interruption policy, recognition, task reasoning, synthesis and transport therefore remain separately observable decisions.

## Problem decomposition

| Layer | Independent decision | Serious families | Current boundary |
| --- | --- | --- | --- |
| channel | preserve or emulate the audio actually received | WebRTC wideband; SIP/8 kHz G.711; packet loss/jitter; resampling; echo/noise suppression | local text-mode session; no phone network |
| speech activity | decide whether a frame contains speech | energy/RMS; WebRTC VAD; neural VAD such as Silero/TEN | LiveKit default/profile behavior; no scored audio |
| turn completion | decide whether a pause ends the caller's turn | fixed silence; STT endpoint; semantic text model; audio-semantic model | `inference.TurnDetector()` in optional hosted profile; no language gate |
| interruption | decide whether new speech should cancel, duck or coexist with agent audio | eager VAD; duration/word gates; semantic/adaptive barge-in; full-duplex floor control | framework interruption behavior; simulated timestamp event |
| recognition | convert audio to text and timestamps | hosted streaming ASR; Whisper family; transducer/Conformer; language-specific models | deterministic text echo; optional Deepgram Nova-3 `multi` |
| language route | choose a language/profile without hiding code-switch errors | fixed route; caller selection; language ID; multilingual/code-switch model | one generic hosted profile |
| semantic/task layer | extract facts and authorize tools | transcript normalization; constrained extraction; FAQ retrieval; state machine/tool calls | grounded deterministic booking/CRM path exists |
| synthesis | produce intelligible, timely speech | hosted neural TTS; local ONNX/Supertonic or validated voice models; direct audio model | duration-only simulator; optional Cartesia Sonic |
| dialogue architecture | expose or collapse intermediate evidence | cascaded STT-LLM-TTS; half-duplex; full-duplex speech-to-speech | cascaded LiveKit session |
| evaluation | decide which profile is safe for which language/channel | corpus ASR; entity/task scoring; EOT/interruption suite; native-speaker TTS; end-to-end task runs | contract tests and fixed synthetic latency only |

## Technique families and operating regions

### Deterministic text/timing simulation — `established control`, not speech evidence

The existing no-key profile is the mandatory workflow control. It isolates qualification, FAQ, booking, CRM and handoff semantics from provider availability and makes failures reproducible. It must not be used as ASR, TTS, VAD, turn-taking or phone-latency evidence. LiveKit's own test framework is text-mode; its documentation directs full-audio validation to end-to-end testing.

### Hosted streaming ASR — `established family`, language-specific experiment required

Deepgram Nova-3 documents streaming Lithuanian (`lt`) and English support, but Nova-3 does not include model-native turn detection. Deepgram Flux adds turn detection, yet its published ten-language list omits Lithuanian. The current `language="multi"` setting is therefore not a substitute for fixed `en` and `lt` arms. Azure also documents `lt-LT` realtime STT and is a reasonable hosted challenger if provider breadth is worth the additional adapter and credentials. Provider claims close capability screening, not FirstRing accuracy, entity fidelity, latency or cost.

### Whisper implementations — `established local family`, benchmark rather than rewrite

OpenAI Whisper supplies the multilingual model family; Faster-Whisper is the closest Python/CTranslate2 runtime, with word timestamps and an integrated Silero VAD option, while Whisper.cpp supplies CPU/GPU/quantized deployment and a server/process seam. These are credible local/private controls, but neither is a native low-latency telephone agent by declaration alone. Windowing, VAD, partial stability and finalization policy must be frozen and measured. Faster-Whisper issues and releases also make segmentation/version pinning consequential.

### Conformer/transducer ASR — `established alternative family`

NVIDIA Parakeet-TDT 0.6B v3 explicitly covers English and Lithuanian among 25 European languages and is a strong non-Whisper final-transcript challenger. Nemotron 3.5 ASR has a cache-aware streaming architecture, but its model card places Lithuanian in the “adaptation-ready” tier and recommends fine-tuning before production-quality transcription. It is therefore a streaming research arm, not an out-of-box Lithuanian winner. NeMo is a heavier runtime; adopt it only if the measured accuracy/latency frontier justifies that operational cost.

### Energy/WebRTC VAD — `established cheap control`

WebRTC VAD is a small, fast voiced/unvoiced classifier and works naturally with telephony frames. The maintained `py-webrtcvad-wheels` fork is preferable to the older Python wrapper for a Python experiment. It is a frame-level baseline, not an end-of-turn model, and aggressiveness must be swept per channel.

### Silero and TEN neural VAD — `established candidates`

Silero is already the LiveKit ecosystem's standard local neural VAD and is the first integration candidate. TEN VAD publishes a reproducible open test set and comparison script against WebRTC and Silero, advertises 10/16 ms frames and 16 kHz input, and explicitly says its threshold needs domain tuning. Vendor-reported superiority is not transferable to Lithuanian telephone calls; both should run through the same frozen channel/turn suite. No project-specific VAD should be written.

### Silence endpointing — `established fallback`, especially for unsupported languages

A VAD plus a fixed minimum silence delay is language-agnostic, inspectable and the required Lithuanian control. It reacts to silence rather than semantic completion, so too-short thresholds cut off clause-internal pauses and too-long thresholds make the agent sluggish. Sweep thresholds against real Lithuanian turns instead of borrowing an English default.

### Semantic/audio turn detection — `established family`, coverage-limited

LiveKit's current audio turn detector combines acoustic and semantic signals and publishes `eot-bench`, which scores every candidate pause in natural task conversations. Its 14-language list includes English but not Lithuanian. Pipecat Smart Turn v3.2 similarly supports 23 languages but omits Lithuanian. Both are valid English challengers and useful implementation references; neither may silently handle Lithuanian. `eot-bench` is the preferred harness to refit, augmented with a project-owned Lithuanian dual-channel set.

### Interruption policy — `distinct from VAD and turn completion`

Eager interruption on any voiced frame minimizes barge-in delay but treats coughs, backchannels and echo as commands to stop. Duration/word gates reduce false cancellations at the cost of slower real interruptions. LiveKit's adaptive interruption model distinguishes semantic interruption from backchannel behavior, but is cloud-dependent and remains subject to supported-language and task evidence. Score interruption precision/recall, cancellation latency and resume behavior separately from EOT accuracy.

### Hosted Lithuanian TTS — `established capability`, native evaluation required

Azure publishes `lt-LT-OnaNeural` and `lt-LT-LeonasNeural`; Google publishes Lithuanian Standard and Chirp 3 HD voices. These close basic availability. The current Cartesia Sonic-3 family publishes 42 languages but omits Lithuanian, so the existing hosted profile is English-only unless Cartesia changes its documented coverage. Voice samples and vendor latency claims do not close FirstRing pronunciation, number/date/name intelligibility, streaming first-audio latency or native preference.

### Local Lithuanian TTS — `established candidate`, quality unknown

Supertonic 3 publishes an ONNX/on-device runtime and a 31-language list that explicitly includes Lithuanian, making it the defensible local/private control. Its voice quality, Lithuanian pronunciation and first-audio latency remain untested in FirstRing. Piper is healthy and lightweight, but the official voice index has no Lithuanian voice. Meta MMS broadly advertises more than 1,100 TTS languages, yet its exact published TTS list does not contain Lithuanian; broad family coverage is not an LT artifact. Training a new voice is outside this slice and outside the first experiment.

### Cascaded STT-LLM-TTS — `preferred evidence-bearing architecture`

A cascade exposes the transcript, language, model version, entity extraction, tool request and synthesized text. That evidence is valuable for a receptionist whose booking and CRM effects must be defended. Its costs are accumulated latency and error propagation. Preserve it as the primary architecture while optimizing each measured stage; do not collapse the path merely because a speech-to-speech demo sounds smoother.

### Full-duplex speech-to-speech — `established research family`, deferred challenger

Moshi and PersonaPlex are maintained open implementations of simultaneous listen/speak dialogue. Full-Duplex-Bench and newer task-grounded work show that overlap, backchannels, pause handling, interruptions and tool completion must be evaluated together; recent results also show substantial task failure under realistic audio. The open models do not establish Lithuanian task performance, and unified audio can obscure what the model heard. Admit a direct-audio challenger only if it supports tool receipts, a shadow transcript and the same booking/CRM oracle. Do not replace the cascade first.

### Controlled channel degradation — `established test method`

Use FFmpeg for 8 kHz mono G.711 μ-law/A-law round trips and deterministic resampling, and audiomentations for frozen noise, impulse response, clipping, gain and missing-span transforms. These maintained tools are preferable to custom DSP. Real telephone recordings remain necessary because synthetic transforms cannot reproduce carrier jitter, echo cancellation and microphone behavior completely.

### Corpus, task and human evaluation — `joint requirement`

Common Voice 25 Lithuanian contains 24,859 scripted clips, 35.24 recorded hours and 28.39 validated hours from 331 speakers. FLEURS supplies roughly 12 hours for each of 102 languages and enables parallel EN/LT comparison. Both are read-speech corpora; a 2025 audit found material quality problems in multilingual datasets, so neither is a production proxy. Add speaker-disjoint FirstRing task recordings with names, Lithuanian diacritics, dates, phone numbers, addresses, code-switching, hesitation, corrections and interruptions. Report WER/CER, critical-entity exact accuracy, EOT/interruption errors, latency distributions, real-time factor, task completion and native-speaker TTS judgments.

## Search protocol and saturation

- Search date: 2026-08-05.
- Sources: current official LiveKit/Deepgram/Azure/Google/Cartesia documentation, Mozilla and Google dataset records, primary papers/model cards, and maintained GitHub repositories.
- Main window: 2024-2026, retaining older model papers, standards and corpora when still authoritative.
- Explicit exclusions: license research or ranking; popularity-only selection; provider claims treated as local results; broad “multilingual” labels without an `en`/`lt` coverage check.

| Iteration | Query family | New decision-relevant family |
| ---: | --- | --- |
| 0 | plan-derived ASR, VAD, EOT, interruption and TTS | initial family map |
| 1 | current LiveKit testing/turn/interrupt documentation | audio-test boundary; audio EOT; adaptive interruption |
| 2 | Deepgram/Azure/Google/Cartesia language support | provider capability split; Cartesia/Flux Lithuanian gaps |
| 3 | Whisper, Parakeet, Nemotron and local deployment | non-Whisper and cache-aware streaming ASR |
| 4 | WebRTC, Silero, TEN, Smart Turn and eot-bench | reproducible VAD/EOT component set |
| 5 | Supertonic, MMS, Piper and Lithuanian TTS artifacts | local Supertonic control; exact MMS/Piper gaps |
| 6 | Moshi, PersonaPlex and full-duplex benchmarks | direct-audio architecture and evidence risks |
| 7 | Common Voice/FLEURS quality, telephony degradation and TTS evaluation | corpus-quality limitation and channel/native review contract |
| 8 | explicit alternatives and contrary evidence | no new top-level family; refinements only |

Iteration 8 added no top-level family after the architecture, language, channel and evaluation alternatives above were incorporated. Technique-family saturation is `PASS` for the dated FirstRing scope.

## Primary anchors

- [LiveKit agent testing](https://docs.livekit.io/agents/start/testing/)
- [LiveKit audio turn detector and eot-bench](https://docs.livekit.io/agents/logic/turns/turn-detector/)
- [LiveKit turn-taking tuning](https://docs.livekit.io/agents/logic/turns/tuning/)
- [LiveKit adaptive interruption handling](https://docs.livekit.io/agents/logic/turns/adaptive-interruption-handling/)
- [Deepgram models and languages](https://developers.deepgram.com/docs/models-languages-overview/)
- [Deepgram Flux multilingual languages](https://developers.deepgram.com/docs/flux/language-prompting)
- [Azure Speech language and voice support](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support)
- [Google Cloud TTS voices](https://docs.cloud.google.com/text-to-speech/docs/list-voices-and-types)
- [Cartesia model language list](https://docs.cartesia.ai/build-with-cartesia/tts-models/older-models)
- [NVIDIA Parakeet-TDT 0.6B v3 model card](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3)
- [NVIDIA Nemotron 3.5 streaming ASR model card](https://huggingface.co/nvidia/nemotron-3.5-asr-streaming-0.6b)
- [Supertonic on-device multilingual TTS](https://github.com/supertone-inc/supertonic)
- [Meta MMS exact TTS language-list instructions](https://github.com/facebookresearch/fairseq/tree/main/examples/mms)
- [Mozilla Common Voice 25 Lithuanian](https://mozilladatacollective.com/datasets/cmn2cxca301dro107ucz5j8ey)
- [FLEURS paper](https://arxiv.org/abs/2205.12446)
- [Multilingual speech dataset quality audit](https://aclanthology.org/2025.acl-long.370/)
- [Full-Duplex-Bench](https://arxiv.org/abs/2503.04721)
- [Full-Duplex-Bench v3](https://arxiv.org/abs/2604.04847)
- [FirstRing code reuse audit](GITHUB_IMPLEMENTATION_AUDIT.md)
