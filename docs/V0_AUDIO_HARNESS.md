# V0 deterministic audio harness

## Acceptance contract

V0 proves that FirstRing can ingest committed PCM/WAV bytes, preserve a single
scripted event timeline, execute its existing deterministic booking/CRM/handoff
interfaces, and emit a byte-stable normalized receipt. It does **not** measure
ASR, VAD, end-of-turn, TTS, voice, telephone, provider, model, latency, or
production quality.

The committed, versioned JSON Schema and manifest are the construction oracle.
They pin the WAV SHA-256 and format, exact transcript finals, critical entities,
task facts, scripted event relations, and the expected business effect. The harness checks those facts
against actual `CallEngine` execution and excludes UUIDs, delivery action IDs,
wall-clock time, network timing, provider identifiers, and model inference from
the normalized artifact.

## Rerun

```powershell
$env:PYTHONPATH = "src"
python scripts/run_v0_audio_gate.py `
  --receipt docs/evidence/v0-audio/receipt.json `
  --mutation-report docs/evidence/v0-audio/mutation-report.json
```

The gate passes only if the clean control passes and all seven frozen faults are
killed: dropped final transcript, final-before-partial ordering, erased critical
entity, clause-internal pause promoted to end-of-turn, missing interruption
cancellation, wrong booking/CRM result, and duplicate effect receipt.

`scripts/generate_v0_fixture.py` deterministically regenerates the stereo,
16-bit, 8 kHz PCM WAV. Its two tone lanes mark scripted caller and agent activity;
they are not recordings and must not be presented as speech-recognition evidence.

## Test-method choices

The gate adopts construction-known truth, operator/relation assertions,
information asymmetry between fixture authoring and execution, a clean control,
and explicit mutation kills. It rejects model judges, judge voting,
model-generated labels, and probabilistic output as V0 oracles. Those additions
would increase cost and ambiguity without improving this deterministic contract.
