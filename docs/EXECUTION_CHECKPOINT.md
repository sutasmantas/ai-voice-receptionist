# FirstRing systematic technique checkpoint

- Date: 2026-08-05
- Worktree: `portfolio_demos/worktrees/voice_receptionist_technique_dossier`
- Branch: `agent/voice-receptionist-technique-dossier`
- Base: `79a92a46971f3ecb8a5ba2e596a2e8b2b92f97a0`
- Dossier commit: `16445861c3052d0ae02c52ce0117b2fd50e6fc91`
- Gate: systematic evidence `PASS`; experiment and overall technique ceiling
  remain `PARTIAL`
- Artifacts: `TECHNIQUE_TAXONOMY.md`, `EVIDENCE_MATRIX.csv`,
  `GITHUB_IMPLEMENTATION_AUDIT.md`, `BENCHMARK_DESIGN.md`,
  `RESEARCH_DECISION.md`, and `docs/EXPERTISE_NOTES.md`
- GitHub-first decision: reuse maintained ASR, VAD, EOT, TTS and channel
  components; custom work is limited to adapters, manifests, receipts and
  task/entity scorers
- Corrected compatibility boundary: the current generic hosted profile is not
  bilingual evidence; LiveKit audio EOT and Cartesia omit Lithuanian, while an
  exact MMS/Piper artifact check also rejected both as LT controls; Supertonic
  3 is the local LT TTS candidate
- Baseline verification:
  - `.venv\\Scripts\\python.exe -m ruff check .` — PASS
  - `.venv\\Scripts\\python.exe -m ruff format --check .` — PASS (19 files)
  - `.venv\\Scripts\\python.exe -m mypy` — PASS (14 source files)
  - `.venv\\Scripts\\python.exe -m pytest --cov=firstring --cov-report=term-missing`
    — PASS (16 tests, 89.13% coverage)
  - evidence-matrix CSV parse — PASS (29 rows, 14 columns)
- Boundaries: no dataset download, audio capture/generation, model inference,
  provider call, SIP/phone test, dependency/application change, UI/polish,
  merge, push or publication was performed
- Remaining limitations: no measured EN/LT ASR, VAD, EOT, interruption, TTS,
  duplex, telephone, latency, cost, native preference or production result;
  V0-V5 are frozen designs only
- Exact next action: update the central expertise index and portfolio restart
  controls to mark FirstRing systematic research complete and point to
  Printline; then stop before Printline or any experiment/depth work

## Previous P5 checkpoint

- Date: 2026-08-03
- Branch: `agent/voice-receptionist-p5`
- Foundation: `livekit-examples/agent-starter-python` at
  `7c0af539fe065e262f31942715f5f97e1579fd78`
- Evidence commit: `2db8a643b930f6dedb806bca8a61f376b7b19306`
- Gate-close branch commit: `1a3fa50dd34c0d2e64eae2f6623b100d4615cf43`
- Local main merge commit: `e6f2b1c759265ee889d7baeafbeee5f6dc23f68c`
- Gate: all minimum referenceable P5 rows PASS
- Tests: 16 passed, 89.13% coverage, ResourceWarning promoted to error
- Clean checkout: Ruff, formatting, strict mypy, tests, deterministic demo,
  wheel/sdist build, and Twine validation PASS
- Container: digest-pinned build PASS; non-root `app`; healthy; `/health` and
  `/` PASS
- Responsive evidence: 1440, 1024, and 390 px Playwright Chromium captures
  committed under `docs/screenshots/`
- Boundaries: no real phone network, hosted inference/speech, external SaaS,
  production load, or production latency exercised
- Phase 4 shared verification extension: ProofGrid wheel SHA-256
  `8267749b224b860e6ef774f5097539bc28a3abd7e85e11900862943ef9ce1001`;
  Inspect AI commit `cb00efcd12dfbf3e44f486648e05e54f1337fe9a`;
  baseline 4/4 PASS; fail-open mutant 3/4 with only `unknown-faq` rejected;
  `--require-pass` returned the expected exit code 2 for the mutant
- Phase 4 native gate: Ruff, format check, strict mypy, 18 tests, sdist/wheel
  build, and Twine validation PASS
- Evidence: `docs/evidence/inspect/baseline` and
  `docs/evidence/inspect/fail-open-mutant` preserve raw Inspect JSON logs and
  normalized ProofGrid results; generated SQLite state is intentionally ignored
- Next action: integrate the verified extension into local `main`; hosted
  GitHub execution remains a deferred cross-portfolio follow-up
