# FirstRing research decision

Date: 2026-08-05

## Outcome

The systematic evidence gate is `PASS`. Experiment and overall technique-ceiling gates remain `PARTIAL`: V0-V5 are frozen designs, not results.

The current deterministic LiveKit/workflow profile remains the honest non-audio control. The first controlled depth work is V0 and V1: build a real-audio receipt harness, then compare fixed English and Lithuanian ASR profiles under clean and telephone-degraded conditions. V2 separates VAD from EOT; V3 tests false and true barge-in; V4 tests TTS with native speakers; V5 promotes only a complete language/channel profile.

There is no evidence-based reason to implement speech models, VAD, DSP or a new agent framework from scratch. There is also no basis to keep FirstRing's current generic hosted profile as a bilingual claim: Nova-3 can transcribe Lithuanian, but the configured LiveKit turn detector and Cartesia TTS do not document Lithuanian support.

## Retained decisions

| Decision | Disposition |
| --- | --- |
| deterministic no-key workflow and business-effect tests | invariant control; explicitly non-audio |
| LiveKit Agents | retain framework and session/tool contract |
| fixed `en` and `lt` profiles | mandatory; `multi` is an additional code-switch arm only |
| Deepgram Nova-3 | hosted ASR experiment; external support does not select a winner |
| Azure STT | optional hosted challenger if a second provider is affordable |
| Faster-Whisper or Whisper.cpp | one pinned local/private Whisper arm, chosen by deployment seam |
| Parakeet-TDT 0.6B v3 | non-Whisper local final-transcript challenger |
| Nemotron 3.5 streaming ASR | research arm only; Lithuanian is adaptation-ready, not production-ready |
| WebRTC VAD | cheap frame-level control |
| Silero VAD | first neural VAD integration candidate |
| TEN VAD | challenger through the same project corpus; vendor benchmark is not a local result |
| LiveKit audio turn detector | English EOT challenger; prohibited for Lithuanian claims |
| Smart Turn | English reference/challenger only; no Lithuanian coverage |
| VAD plus fixed silence | mandatory Lithuanian EOT control and fallback |
| eager/duration-word interruption | local measurable controls |
| LiveKit adaptive interruption | conditional cloud challenger; not assumed bilingual |
| Azure and Google Lithuanian TTS | hosted V4 candidates |
| Cartesia Sonic | English-only candidate under current published coverage |
| Supertonic 3 | local/private V4 LT candidate |
| Meta MMS TTS | reject for LT because the exact published TTS list omits Lithuanian |
| Piper | reject for Lithuanian until an official or validated LT voice exists |
| cascaded STT-LLM-TTS | primary evidence-bearing architecture |
| Moshi/PersonaPlex/direct speech-to-speech | deferred until language, tool receipt and task-oracle admission gates pass |
| audiomentations and FFmpeg | reuse for frozen degradation recipes; do not write custom DSP |

## Exact next controlled work

1. V0: add real PCM/WAV input, event timestamps, model/config pins, transcript revisions and tool/effect receipts without changing the deterministic demo.
2. V1: run fixed `en` and `lt` ASR arms on speaker-disjoint public plus task audio, including G.711/noise/clipping/packet-gap conditions.
3. V2 only after the audio manifest is frozen; score WebRTC/Silero/TEN and supported-language EOT independently.
4. V3 only with dual-channel overlap annotations and audible-output cancellation/resume receipts.
5. V4 only with native Lithuanian and English reviewers and blind randomized samples.
6. V5 promotes a whole profile only after safety, task, latency and reproducibility gates pass.

No experiment, dependency/application change, provider call, audio generation, UI work, visual polish, merge, push or publication was performed in this slice.

## Eleven systematic evidence gates

| Gate | Status | Evidence |
| --- | --- | --- |
| Problem decomposition | PASS | channel through end-to-end evaluation layers in `TECHNIQUE_TAXONOMY.md` |
| Search protocol | PASS | dated official/primary sources and nine reproducible iterations |
| Survey coverage | PASS | hosted/local ASR, three VAD levels, silence/semantic/audio EOT, interruption, local/hosted TTS and cascaded/direct-audio architectures |
| Benchmark coverage | PASS | public EN/LT speech, project task audio, telephone degradations, dual-channel turns and native TTS review in V0-V5 |
| Existing-answer search | PASS | component implementations are separated from FirstRing-specific adapters and scorers |
| Technique-family saturation | PASS | final alternative/contrary-evidence iteration added no top-level family |
| Candidate comparison | PASS | `EVIDENCE_MATRIX.csv` |
| Contrary evidence | PASS | read-speech transfer, dataset quality, language-coverage, vendor-benchmark and direct-audio observability limits |
| Implementation evidence | PASS | exact GitHub pins, health and seams in `GITHUB_IMPLEMENTATION_AUDIT.md` |
| Portfolio fit | PASS | creates defensible multilingual voice evaluation depth without duplicating the workflow/CRM evidence already present |
| Review status | PASS | all unrun metrics and provider behavior remain explicitly unknown |

## Claim boundary

Defensible now: FirstRing proves its bounded deterministic receptionist, booking, CRM and handoff path and now has a systematic, GitHub-first plan for real EN/LT audio, language-specific endpointing, interruption, TTS and complete-profile promotion.

Not defensible now: English or Lithuanian ASR/TTS quality, semantic Lithuanian turn detection, phone-network behavior, hosted-provider latency/cost, full-duplex quality, native-speaker preference, production scale, or client outcome uplift.
