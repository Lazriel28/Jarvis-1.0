from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ToolCall:
    name: str
    args: dict = field(default_factory=dict)


class Memory:
    def __init__(self) -> None:
        self.messages: List[str] = []

    def remember(self, message: str) -> None:
        self.messages.append(message)
        if len(self.messages) > 25:
            self.messages = self.messages[-25:]

    def get_recent(self, count: int = 5) -> List[str]:
        return self.messages[-count:]


class Agent:
    def __init__(self, model_manager, tool_runner) -> None:
        self.model_manager = model_manager
        self.tool_runner = tool_runner
        self.memory = Memory()

    def ask(self, prompt: str, confirm_tool: bool = False) -> str:
        self.memory.remember(prompt)

        prompt_lower = prompt.lower()
        if "time" in prompt_lower:
            return self.tool_runner.execute("get_time", confirmed=confirm_tool)
        if "date" in prompt_lower:
            return self.tool_runner.execute("get_date", confirmed=confirm_tool)
        if "system info" in prompt_lower or "system" in prompt_lower and "info" in prompt_lower:
            return self.tool_runner.execute("system_info", confirmed=confirm_tool)
        if "open" in prompt_lower and "http" in prompt_lower or "open" in prompt_lower and ".com" in prompt_lower:
            url = "https://www.google.com"
            if "github" in prompt_lower:
                url = "https://github.com"
            return self.tool_runner.execute("open_browser_url", {"url": url}, confirmed=confirm_tool)

        final_prompt = "\n".join(self.memory.get_recent(6))
        response = self.model_manager.generate(final_prompt, history=self.memory.get_recent(6))
        return response


if __name__ == "__main__":
    print("Agent ready.")
