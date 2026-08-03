# FirstRing claim ledger

| Claim | Evidence | Safe wording | Do not claim |
| --- | --- | --- | --- |
| Voice-agent runtime boundary | inherited LiveKit `AgentServer`/`AgentSession`; no-key `AgentSession.run` test with pinned fake LLM | built on the official LiveKit Python agent starter and verified its text-session seam without credentials | deployed LiveKit Cloud agent or production voice traffic |
| Streaming contracts | `StreamingStt`, `ReasoningAdapter`, `StreamingTts`; deterministic partial/final transcript and timed audio chunks | implemented and tested streaming speech/reasoning/synthesis contracts in a deterministic call simulator | measured hosted STT/TTS quality |
| Grounded receptionist behavior | known/unknown FAQ fixtures with hard threshold and explicit transfer | answers from an approved FAQ set and fails closed to human transfer | general RAG or broad factual accuracy |
| Turn handling | timed fixtures and `assistant_interrupted` splice evidence | simulates and evaluates caller interruption and turn latency | real acoustic VAD/barge-in performance |
| Booking/CRM | parity-protected LeadDock adapters; one booking across repeated intent | integrates deterministic CRM mapping and idempotent, collision-safe calendar booking | Google Calendar, Salesforce, HubSpot, or another named SaaS integration |
| Durable handoff | DeliveryGuard action/attempt store, three bounded failures, dead-letter and replay | produces structured call summaries with idempotent webhook retry, dead-letter, and replay | delivery to a real external CRM in this demo |

## Unsupported boundary

No phone number, SIP/PSTN provider, hosted model, hosted speech provider,
external CRM/calendar, production availability, production security posture, or
production latency has been exercised. Real telephony remains optional future
integration work and is deliberately not required by P5.
