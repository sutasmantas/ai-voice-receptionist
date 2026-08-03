# FirstRing project start

## 1. Restart boundary

- repository: `portfolio_demos/voice_receptionist`
- baseline branch and commit: `main` at
  `7c0af539fe065e262f31942715f5f97e1579fd78`
- implementation branch: `agent/voice-receptionist-p5`
- assigned isolated worktree:
  `portfolio_demos/worktrees/voice_receptionist_p5`
- owner/session: primary Codex session for P5
- repositories/worktrees that are read-only: `lead_dock` at
  `3ecc87849c0e0cfc67dad1b2b89721e56d261740`, `delivery_guard` at
  `4fd8eaa72cda6aff551fbec095e61b7b32d35fcb`, and every other portfolio
  repository/worktree
- exact next action: implement the deterministic timed-event domain and its
  tests, then attach the adopted booking and delivery contracts

This worktree must not switch branches or be shared with another active
session.

## 2. Client outcome and non-duplication

- one client-purchased outcome this project proves: a simulator-first voice
  receptionist that answers only grounded business questions, handles
  interruption and operating rules, books exactly once, and hands a structured
  call summary to a generic CRM/webhook boundary
- existing portfolio evidence closest to it: LeadDock proves deterministic lead
  intake, CRM mapping, and calendar booking; Relay proves tool execution and
  approval-aware workflow inspection
- mechanism or deliverable that is genuinely new: timed conversational events,
  turn interruption, partial/final transcript contracts, explicit FAQ
  not-found behavior, voice-specific entity and latency evaluation, and a
  replayable call score
- why this is better coverage than deepening an existing project: it adds a
  defensible voice-agent and real-time workflow surface without pretending a
  telephony provider was exercised

## 3. GitHub foundation comparison

Licenses were not researched, compared, filtered, or ranked. These projects are
private working evidence for the user.

| Candidate | Repository | Activity/version checked | Central behavior reusable for this MRE | Adaptation cost/risk | Decision |
| --- | --- | --- | --- | --- | --- |
| LiveKit Python agent starter | `https://github.com/livekit-examples/agent-starter-python` | commit `7c0af539fe065e262f31942715f5f97e1579fd78`, 2026-07-21 | real `AgentServer`/`AgentSession` entrypoint, streaming STT/LLM/TTS assembly, turn detector, console/dev/start modes, Docker packaging | small repository; hosted providers remain optional and credentialed tests must be replaced | adopt |
| Pipecat quickstart | `https://github.com/pipecat-ai/pipecat-quickstart` | commit `65f1caa1ce413aca76619d008cba2a05f3ac4a13`, 2026-03-30 | VAD, STT/LLM/TTS pipeline, Daily/WebRTC runner | single provider-heavy script, no bounded deterministic test core | reject as foundation |
| Pipecat examples | `https://github.com/pipecat-ai/pipecat-examples` | commit `9baf48919b6d3f1ce4d275e8e13d37326d3c2c0f`, 2026-07-27 | PSTN, SIP, and transfer examples | very large integration surface; importing it would add unexercised telephony complexity | consult patterns only |

Selected foundation:

- repository URL: `https://github.com/livekit-examples/agent-starter-python`
- pinned tag/commit: `7c0af539fe065e262f31942715f5f97e1579fd78`
- exact code/package/contracts reused: `src/agent.py` server/session entrypoint,
  `AgentSession` STT/LLM/TTS assembly, LiveKit turn handling, Docker and `uv`
  project shape
- upstream history/identity preservation: the product repository retains the
  full upstream Git history and an `upstream` remote; implementation continues
  on `agent/voice-receptionist-p5`
- why this is faster/safer than starting blank: the foundation already runs the
  central voice-agent lifecycle and provider boundary, leaving portfolio work
  focused on deterministic behavior and evidence

## 4. Component-level GitHub reuse audit

| Proposed component | GitHub candidates checked | Decision | Exact reused surface or custom boundary | Integration cost | Why this is lower-cost than alternatives |
| --- | --- | --- | --- | --- | --- |
| Voice runtime and provider assembly | LiveKit Agents `1.6.7`; Pipecat `1.7.0` | adopt | pin `livekit-agents==1.6.7`; keep the inherited server/session boundary | one runtime rather than two; provider credentials remain optional | already matches the selected repository and avoids a second frame/runtime model |
| No-key agent test seam | LiveKit Agents commit `bbf163fe1c2cbe1b46079e0ed04ccfca5a259c59`; Pipecat evals at `b114a367a32166207712e8a9c352215a6e24a0db` | refit | refit LiveKit's small deterministic fake-LLM/session pattern; do not copy its large fake-audio suite | bounded seam protected by local contract tests | exercises the adopted runtime without keys or a second evaluation framework |
| Booking and CRM contracts | LeadDock `3ecc87849c0e0cfc67dad1b2b89721e56d261740`; generic calendar/CRM SDKs | refit | preserve the exact `Booking`, `LocalCalendarAdapter`, and `LocalCrmAdapter` behavior with source provenance and focused parity tests | tiny adapter surface; no SaaS SDKs or credentials | removes collision, timezone, idempotency, and CRM mapping work already proven locally |
| Durable webhook handoff | DeliveryGuard `0.1.0` at `4fd8eaa72cda6aff551fbec095e61b7b32d35fcb`; ad-hoc retries | adopt | consume `DeliveryStore`, `DeliveryExecutor`, `RetryPolicy`, and adapter protocol from a pinned local wheel | one coherent package with SQLite state and retry tests | removes retry, idempotency conflict, dead-letter, replay, and redaction responsibilities |
| FAQ grounding | RapidFuzz `3.14.5` tag `edf9f3c2d016c878dae1511301f8b4a501bba871`; rank-bm25 and embedding stacks | adopt | token-set match against a small explicit FAQ corpus with a hard threshold and `not_found` result | one small dependency; no index/model lifecycle | the corpus is intentionally small and must fail closed, so retrieval infrastructure would add more glue than capability |
| Timed event/state reducer | `transitions` `0.9.3` tag `f970687f48f807dd5974f59c4d76abed2bd1e7bd`; `python-statemachine` `3.2.1`; Pipecat frames | custom | typed immutable call/turn events and a reducer limited to timestamp validation, interruption splicing, metrics, and outcome state | about one focused module; no runtime callbacks or graph lifecycle | state-machine packages do not provide timed media semantics and would require duplicate event bookkeeping |
| Call/evidence persistence | DeliveryGuard SQLite store; SQLAlchemy/SQLModel | custom | stdlib SQLite tables for call runs and immutable event JSON only | small fixed schema and no ORM migrations | another ORM would exceed the fixed evidence schema and duplicate an existing SQLite dependency boundary |
| API and schema boundary | FastAPI/Pydantic; Flask/Marshmallow | adopt | typed scenario/run/replay HTTP endpoints and validation | established dependency already compatible with LiveKit | avoids hand-written request validation and keeps the boundary inspectable |
| Structural UI | ReactFlow, chat UI kits, data grids | custom | server-rendered HTML/CSS/JS call-score ruler and outcome ticket | one screen, no frontend build/runtime | generic chat/graph/table kits would force the wrong interaction model and add upgrade surface |

- component audit completed before implementation: yes, 2026-08-03
- selected reusable components and pins: LiveKit starter commit `7c0af539`,
  `livekit-agents==1.6.7`, LiveKit deterministic test pattern commit
  `bbf163fe`, LeadDock contracts commit `3ecc878`, DeliveryGuard `0.1.0`
  commit `4fd8eaa`, and RapidFuzz `3.14.5`
- deliberately custom components and decision evidence: the timed reducer,
  fixed call store, and one-screen call-score UI have project-specific behavior
  smaller than the glue required by the compared libraries
- overlapping candidates rejected to avoid integration/upgrade burden: Pipecat
  runtime/evals, hosted calendar/CRM SDKs, rank-BM25/embedding stores, generic
  state-machine packages, an ORM, ReactFlow, chat kits, and data grids

## 5. Distinct visual direction

| Existing project | Screenshot inspected | Spatial model | Navigation | Palette family | Typography character | Geometry/surface model | Dominant interaction | Candidate differences |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Relay | `support_automation/docs/screenshots/relay-case-workspace.png` | three-column case workspace | dark left rail plus tabs | white/navy/teal | compact product sans | rounded bordered cards | inspect and approve queued work | no rail, no columns, no approval cards |
| LeadDock | `lead_dock/docs/leaddock-1440.png` | arrival strip over appointment ledger | top arrival selection | lavender/plum/coral | condensed ledger display | boxed rows and receipt tape | select lead then book a slot | time ribbon is conversational, not a schedule ledger |
| PipelineForge | `pipeline_forge/docs/screenshots/pipelineforge-1440.png` | source/destination dossier and reconciliation table | horizontal stage rail | newsprint/black/cobalt | editorial serif plus mono | ruled register sheets | compare source and destination | no comparison table or document-register layout |
| Printline | `generative_workflow/docs/screenshots/printline-workstation-1440.png` | dark artboard with right control deck | workstation regions | charcoal/lime/coral | industrial mono/sans | square machine panels | configure then render | bright continuous score; no artboard or control deck |

- comparison projects/screenshots reviewed: Relay, LeadDock, PipelineForge, and
  Printline rendered working states at desktop width
- product/audience metaphor: a hotel front-desk switchboard crossed with a
  musical call score; an operator can see precisely when caller, agent, and
  tools acted
- layout structure: a full-width horizontal time ruler and stacked caller /
  receptionist / tool ribbons, followed by a detachable outcome ticket; no
  persistent sidebar
- palette: sunlit ivory ground, cobalt caller ribbon, tomato receptionist
  ribbon, mustard tool markers, near-black ink
- typography character: bold grotesk display labels with compact neutral sans
  transcript text; no editorial serif or terminal-heavy hierarchy
- primary interaction pattern: run or scrub a fixed scenario, then select a
  timed turn/interruption marker to inspect captured entities, latency, and
  outcome
- explicit patterns avoided because another project already uses them:
  sidebars, three-column workspaces, chat bubbles, KPI-card grids, appointment
  ledgers, source/destination tables, dark artboards, and right control decks
- 1440 px first-viewport evidence: `docs/screenshots/firstring-1440.png`,
  Playwright Chromium capture of the working successful-booking fixture; PASS
- 1024 px responsive evidence: `docs/screenshots/firstring-1024.png`,
  Playwright Chromium capture with score, inspector, and outcome visible; PASS
- 390 px responsive evidence: `docs/screenshots/firstring-390.png`, Playwright
  Chromium capture with three readable timed event columns and stacked evidence;
  PASS
- closest visual neighbor and why this is not a reskin: LeadDock also exposes
  time, but its working surface is a vertical availability ledger; FirstRing's
  central object is a continuous conversational score whose interrupted turns
  are visibly spliced and inspected

The rejected `ui_design_previews/rendered/voice.png` direction is a dark radial
AI stage with transcript and KPI cards. It is too close to the portfolio's dark
workstation products and is not the implementation reference.

## 6. Minimum referenceable evidence contract

| Gate | Observable acceptance evidence | Status |
| --- | --- | --- |
| Central similarity | inherited LiveKit server/session runs with pinned runtime and preserved upstream history | PASS |
| Component-level reuse decisions | every substantial subsystem audited before implementation in this record | PASS |
| Working vertical slice | deterministic inbound scenario reaches grounded answer, one booking, summary, and handoff | PASS |
| No-key deterministic proof | fixtures run without provider credentials and exercise timed STT/LLM/TTS contracts | PASS |
| Invalid input and abuse behavior | invalid timestamps/entities/scenarios fail explicitly; opt-out prevents booking/handoff | PASS |
| Provider/tool failure and retry/refusal/handoff | FAQ not-found and after-hours transfer; injected adapter failure dead-letters and replays | PASS |
| Focused mechanism tests | turn/interruption/entity/latency/booking/delivery contract tests pass | PASS |
| Clean-checkout quickstart | documented install/demo/test/build succeeds from clean detached checkout | PASS |
| Cover-letter claim ledger | claims name only exercised LiveKit-compatible, simulator, booking, and webhook behavior | PASS |
| Honest unsupported-claim boundary | no real telephony, hosted provider, production latency, or external SaaS claim | PASS |

Only all `PASS` closes P5. Decorative polish, extra providers, and real
telephony are outside this slice.

## 7. Verification and handback

- static/type/lint command: `.venv/Scripts/python -m ruff check src tests`,
  `.venv/Scripts/python -m ruff format --check src tests`, and
  `.venv/Scripts/python -m mypy -p firstring`; PASS in the detached checkout
- focused tests: `.venv/Scripts/python -m pytest -q -W
  error::ResourceWarning --cov=firstring --cov-report=term-missing`; 16 passed,
  89.13% total coverage, zero warnings
- integration/demo command: `.venv/Scripts/firstring-demo --scenario
  successful-booking --database runtime/clean-demo.sqlite3`; booked, delivery
  state `delivered`, and entity accuracy `1.0`; PASS
- build/package command: `.venv/Scripts/python -m build` and
  `.venv/Scripts/python -m twine check dist/*`; wheel and sdist PASS without
  warnings
- reused-component contract tests and pin/upgrade boundary:
  `tests/test_reuse_contracts.py` verifies the DeliveryGuard wheel SHA-256,
  LeadDock booking replay/collision, CRM mapping, and IANA timezone behavior;
  `tests/test_agent.py` runs LiveKit `AgentSession` with the pinned fake-LLM
  pattern and no provider credentials
- branch and evidence commit: `agent/voice-receptionist-p5` at `2db8a643b930f6dedb806bca8a61f376b7b19306`;
  this gate-close document is the following commit
- clean state: clean detached checkout at `2db8a643b930f6dedb806bca8a61f376b7b19306`
  after install, tests, demo, wheel/sdist build, and Twine validation
- known boundaries: no real phone network, hosted inference, hosted speech,
  production latency, or external CRM/calendar exercised
- container evidence: digest-pinned Python `3.13.5` image built as
  `firstring:p5`; non-root user `app`, Docker health `healthy`, `/health` JSON
  PASS, and `/` HTTP 200
- exact next portfolio action: merge locally, update the central checkpoint,
  and stop mandatory technical expansion; no polish or new project begins
