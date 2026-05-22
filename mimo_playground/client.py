"""MiMo API client with reasoning trace extraction."""

import os
import json
import time
import httpx
from typing import AsyncGenerator, Optional
from dataclasses import dataclass, field


@dataclass
class ReasoningStep:
    """Single step in the reasoning chain."""
    index: int
    content: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class ReasoningResponse:
    """Full response with separated reasoning and answer."""
    reasoning_steps: list[ReasoningStep]
    answer: str
    model: str
    tokens_used: int = 0
    reasoning_tokens: int = 0
    completion_tokens: int = 0
    elapsed_ms: float = 0


class MiMoClient:
    """Async client for MiMo v2.5 Pro reasoning model."""

    def __init__(
        self,
        api_base: Optional[str] = None,
        api_key: Optional[str] = None,
        model: str = "xmtp/mimo-v2.5-pro",
        max_tokens: int = 8192,
        temperature: float = 0.7,
    ):
        self.api_base = api_base or os.getenv("MIMO_API_BASE", "https://api.xiaomi.com/v1")
        self.api_key = api_key or os.getenv("MIMO_API_KEY", "")
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    async def stream_reasoning(
        self,
        prompt: str,
        system: str = "",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[dict, None]:
        """Stream reasoning response, yielding typed events.

        Yields:
            {"type": "reasoning", "content": "..."} — reasoning chunk
            {"type": "answer", "content": "..."} — answer chunk
            {"type": "done", "data": ReasoningResponse} — final result
            {"type": "error", "message": "..."} — error
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": temperature if temperature is not None else self.temperature,
            "stream": True,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        reasoning_parts = []
        answer_parts = []
        reasoning_steps = []
        current_reasoning = ""
        step_index = 0
        start_time = time.time()
        tokens_used = 0

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                async with client.stream(
                    "POST",
                    f"{self.api_base}/chat/completions",
                    json=payload,
                    headers=headers,
                ) as resp:
                    if resp.status_code != 200:
                        body = await resp.aread()
                        yield {"type": "error", "message": f"HTTP {resp.status_code}: {body.decode()}"}
                        return

                    async for line in resp.aiter_lines():
                        if not line.startswith("data: "):
                            continue
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break

                        try:
                            chunk = json.loads(data_str)
                        except json.JSONDecodeError:
                            continue

                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        usage = chunk.get("usage", {})

                        if usage:
                            tokens_used = usage.get("total_tokens", tokens_used)

                        # MiMo reasoning content (thinking mode)
                        reasoning_content = delta.get("reasoning_content")
                        if reasoning_content:
                            current_reasoning += reasoning_content
                            reasoning_parts.append(reasoning_content)
                            yield {"type": "reasoning", "content": reasoning_content}
                            continue

                        # Regular content (the answer)
                        content = delta.get("content")
                        if content:
                            if current_reasoning and not answer_parts:
                                # Transition: reasoning → answer
                                step_index += 1
                                reasoning_steps.append(ReasoningStep(
                                    index=step_index,
                                    content=current_reasoning.strip(),
                                ))
                                current_reasoning = ""
                            answer_parts.append(content)
                            yield {"type": "answer", "content": content}

            # Finalize
            if current_reasoning:
                step_index += 1
                reasoning_steps.append(ReasoningStep(
                    index=step_index,
                    content=current_reasoning.strip(),
                ))

            elapsed = (time.time() - start_time) * 1000
            response = ReasoningResponse(
                reasoning_steps=reasoning_steps,
                answer="".join(answer_parts),
                model=self.model,
                tokens_used=tokens_used,
                elapsed_ms=round(elapsed, 1),
            )
            yield {"type": "done", "data": response}

        except httpx.ConnectError as e:
            yield {"type": "error", "message": f"Connection failed: {e}"}
        except httpx.TimeoutException:
            yield {"type": "error", "message": "Request timed out (120s)"}
        except Exception as e:
            yield {"type": "error", "message": f"Unexpected error: {e}"}

    async def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> ReasoningResponse:
        """Non-streaming completion — returns full ReasoningResponse."""
        reasoning_steps = []
        answer_parts = []
        current_reasoning = ""
        step_index = 0

        async for event in self.stream_reasoning(prompt, system, temperature, max_tokens):
            if event["type"] == "reasoning":
                current_reasoning += event["content"]
            elif event["type"] == "answer":
                if current_reasoning and not answer_parts:
                    step_index += 1
                    reasoning_steps.append(ReasoningStep(index=step_index, content=current_reasoning.strip()))
                    current_reasoning = ""
                answer_parts.append(event["content"])
            elif event["type"] == "done":
                if current_reasoning:
                    step_index += 1
                    reasoning_steps.append(ReasoningStep(index=step_index, content=current_reasoning.strip()))
                return event["data"]
            elif event["type"] == "error":
                raise RuntimeError(event["message"])

        # Should not reach here, but just in case
        return ReasoningResponse(
            reasoning_steps=reasoning_steps,
            answer="".join(answer_parts),
            model=self.model,
        )
