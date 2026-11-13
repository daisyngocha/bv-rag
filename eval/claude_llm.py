"""Judge Ragas bằng Claude qua Anthropic SDK (không qua LangChain).
Claude Sonnet 5.5 / Haiku 5.5 trả 400 khi có temperature, top_p, top_k → wrapper bỏ qua temperature Ragas truyền vào.
effort và thinking gửi qua extra_body để không phụ thuộc phiên bản SDK.
"""
from __future__ import annotations
import asyncio
import os
from dataclasses import dataclass, field
import anthropic
from langchain_core.outputs import Generation, LLMResult
from ragas.llms import BaseRagasLLM

@dataclass
class ClaudeRagasLLM(BaseRagasLLM):
    model: str = "claude-sonnet-5-5"
    effort: str = "low"
    thinking: dict | None = None  # Sonnet 5.5: {"type": "between_tools"}; Haiku 5.5: {"type": "disabled"}
    max_tokens: int = 4096
    usage: dict = field(default_factory=lambda: {"calls": 0, "input_tokens": 0, "output_tokens": 0})
    client: anthropic.AsyncAnthropic | None = field(default=None, repr=False)

    def __post_init__(self):
        super().__post_init__()
        self.client = self.client or anthropic.AsyncAnthropic(
            api_key=os.environ["ANTHROPIC_API_KEY"], max_retries=5
        )

    async def _one(self, text: str) -> Generation:
        body = {"output_config": {"effort": self.effort}} | (
            {"thinking": self.thinking} if self.thinking else {}
        )
        r = await self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": text}],
            extra_body=body,
        )
        self.usage["calls"] += 1
        self.usage["input_tokens"] += r.usage.input_tokens
        self.usage["output_tokens"] += r.usage.output_tokens
        return Generation(
            text="".join(b.text for b in r.content if b.type == "text"),
            generation_info={"stop_reason": r.stop_reason},
        )

    async def agenerate_text(self, prompt, n=1, temperature=None, stop=None, callbacks=None) -> LLMResult:
        return LLMResult(generations=[[await self._one(prompt.to_string()) for _ in range(n)]])

    def generate_text(self, prompt, n=1, temperature=None, stop=None, callbacks=None) -> LLMResult:
        return asyncio.run(self.agenerate_text(prompt, n))

    def is_finished(self, response: LLMResult) -> bool:
        return all(g.generation_info["stop_reason"] == "end_turn" for g in response.generations[0])
