"""Bounded refit of LiveKit Agents fake_llm.py at commit bbf163fe1c2c."""

from __future__ import annotations

from typing import Any

from livekit.agents.llm import (
    LLM,
    ChatChunk,
    ChatContext,
    ChoiceDelta,
    LLMStream,
    Tool,
    ToolChoice,
)
from livekit.agents.types import (
    DEFAULT_API_CONNECT_OPTIONS,
    NOT_GIVEN,
    APIConnectOptions,
    NotGivenOr,
)


class FakeLlm(LLM):
    def __init__(self, responses: dict[str, str]) -> None:
        super().__init__()
        self.responses = responses

    def chat(
        self,
        *,
        chat_ctx: ChatContext,
        tools: list[Tool] | None = None,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
        parallel_tool_calls: NotGivenOr[bool] = NOT_GIVEN,
        tool_choice: NotGivenOr[ToolChoice] = NOT_GIVEN,
        extra_kwargs: NotGivenOr[dict[str, Any]] = NOT_GIVEN,
    ) -> LLMStream:
        return FakeLlmStream(
            self, chat_ctx=chat_ctx, tools=tools or [], conn_options=conn_options
        )


class FakeLlmStream(LLMStream):
    def __init__(
        self,
        llm: FakeLlm,
        *,
        chat_ctx: ChatContext,
        tools: list[Tool],
        conn_options: APIConnectOptions,
    ) -> None:
        super().__init__(llm, chat_ctx=chat_ctx, tools=tools, conn_options=conn_options)
        self.fake_llm = llm

    async def _run(self) -> None:
        item = self.chat_ctx.items[-1]
        text = item.text_content if item.type == "message" else ""
        response = self.fake_llm.responses.get(text or "", "I do not know.")
        self._event_ch.send_nowait(
            ChatChunk(
                id=str(id(self)),
                delta=ChoiceDelta(role="assistant", content=response),
            )
        )
