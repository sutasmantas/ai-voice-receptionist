from __future__ import annotations

import pytest
from livekit.agents import AgentSession

from agent import Assistant
from tests.fake_llm import FakeLlm


@pytest.mark.asyncio
async def test_livekit_session_runs_without_provider_credentials() -> None:
    fake = FakeLlm(
        {"What are your hours?": "We are open Monday through Friday from nine to five."}
    )
    async with AgentSession(llm=fake) as session:
        await session.start(Assistant(llm=fake))
        result = await session.run(user_input="What are your hours?")

        message = result.expect.next_event().is_message(role="assistant").event()
        assert message.item.text_content == (
            "We are open Monday through Friday from nine to five."
        )
        result.expect.no_more_events()
