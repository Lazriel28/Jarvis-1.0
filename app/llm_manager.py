from __future__ import annotations

import json
import platform
import subprocess
import sys
from typing import Optional

import psutil
import requests

from app.config import CONFIG


class LocalLLM:
    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=3)
            if response.status_code != 200:
                return False
            data = response.json()
            models = [item.get("name") for item in data.get("models", []) if item.get("name")]
            return self.model in models or any(model.startswith(self.model) for model in models)
        except Exception:
            return False

    def generate(self, prompt: str, system_prompt: str = "You are a helpful assistant.") -> str:
        if not self.is_available():
            raise RuntimeError("Ollama model unavailable. Run `ollama pull <model>` or switch to offline mode.")

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
        }

        try:
            response = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get("message", {}).get("content", "").strip() or "I don't have a response right now."
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"LLM request failed: {exc}") from exc


class OfflineFallback:
    def __init__(self) -> None:
        self.memory = []

    def respond(self, prompt: str, history: list[str]) -> str:
        lower = prompt.lower()

        if any(word in lower for word in ["hello", "hi", "hey"]):
            return "Hello. I am Jarvis 1.0. How can I help you today?"
        if "time" in lower:
            import datetime
            return f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}."
        if "date" in lower:
            import datetime
            return f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}."
        if "joke" in lower:
            return "I would tell you a joke, but I am still waiting on my good hardware budget."
        if "system" in lower and "info" in lower:
            return self.system_info()
        if "open" in lower and "github" in lower:
            return "I can open a browser URL, but I need your confirmation before launching it."
        if "bye" in lower or "goodbye" in lower:
            return "Goodbye. I will be here when you need me."

        return "I am in offline mode right now. Ask me for the time, date, or system info, or connect Ollama to enable assistant reasoning."

    def system_info(self) -> str:
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()
            platform_name = platform.platform()
            return (
                f"Platform: {platform_name}\n"
                f"CPU usage: {cpu}%\n"
                f"Memory used: {mem.percent}%"
            )
        except Exception:
            return "System info is unavailable right now."


class ModelManager:
    def __init__(self, config) -> None:
        self.config = config
        self.local_model = LocalLLM(config.ollama_base_url, config.default_model)
        self.fallback = OfflineFallback()

    def generate(self, prompt: str, history: Optional[list[str]] = None) -> str:
        history = history or []
        try:
            if self.config.llm_mode == "local":
                response = self.local_model.generate(prompt, system_prompt="You are Jarvis 1.0, a helpful Windows personal assistant.")
                return response
            return self.local_model.generate(prompt, system_prompt="You are Jarvis 1.0, a helpful Windows personal assistant.")
        except Exception:
            return self.fallback.respond(prompt, history)


class ToolRunner:
    def __init__(self) -> None:
        self._allowed = {
            "get_time",
            "get_date",
            "system_info",
            "open_browser_url",
        }

    def execute(self, tool_name: str, args: dict | None = None, confirmed: bool = False) -> str:
        args = args or {}
        if tool_name not in self._allowed:
            return f"Tool '{tool_name}' is not allowed."
        if tool_name in {"open_browser_url"} and not confirmed:
            return "This action requires explicit confirmation before it can run."

        if tool_name == "get_time":
            import datetime
            return datetime.datetime.now().strftime("%I:%M %p")
        if tool_name == "get_date":
            import datetime
            return datetime.datetime.now().strftime("%A, %B %d, %Y")
        if tool_name == "system_info":
            return OfflineFallback().system_info()
        if tool_name == "open_browser_url":
            url = args.get("url", "https://www.google.com")
            try:
                if sys.platform.startswith("win"):
                    import webbrowser
                    webbrowser.open(url)
                    return f"Opened {url} in your browser."
            except Exception as exc:  # noqa: BLE001
                return f"Could not open browser: {exc}"
            return f"Open {url} in the default browser."
        return "Unknown tool."


if __name__ == "__main__":
    print("Jarvis model manager ready.")
