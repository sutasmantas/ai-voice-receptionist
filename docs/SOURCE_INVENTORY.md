# Source inventory

| Surface | Source | Pin | Local use |
| --- | --- | --- | --- |
| repository foundation | `livekit-examples/agent-starter-python` | `7c0af539fe065e262f31942715f5f97e1579fd78` | Git history, LiveKit agent entrypoint, Docker/CI starting shape |
| voice runtime | `livekit/agents` | package `1.6.7` | `AgentServer`, `AgentSession`, STT/LLM/TTS and turn-handling boundary |
| no-key LLM test pattern | `livekit/agents/tests/fake_llm.py` | `bbf163fe1c2cbe1b46079e0ed04ccfca5a259c59` | bounded fake LLM refit in `tests/fake_llm.py` |
| booking and CRM | local LeadDock | `3ecc87849c0e0cfc67dad1b2b89721e56d261740` | refitted `Booking`, `LocalCalendarAdapter`, `LocalCrmAdapter` with parity tests |
| durable delivery | local DeliveryGuard `0.1.0` | `4fd8eaa72cda6aff551fbec095e61b7b32d35fcb` | vendored wheel SHA-256 `ffad11647eb44bf6f8b4e0c2306ab9466105129afca937dfa780708057fabfec` |
| FAQ match | RapidFuzz | `3.14.5`, tag `edf9f3c2d016c878dae1511301f8b4a501bba871` | small-corpus token-set scoring with hard not-found threshold |

Licenses were not part of candidate discovery or ranking, per the portfolio
project-start policy.
