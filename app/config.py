from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


@dataclass
class Config:
    app_name: str = "Jarvis 1.0"
    default_model: str = os.getenv("DEFAULT_MODEL", "llama3.2")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_base_url: Optional[str] = os.getenv("OPENAI_BASE_URL")
    allow_shell_commands: bool = os.getenv("ALLOW_SHELL_COMMANDS", "false").lower() == "true"
    voice_enabled: bool = True

    @property
    def llm_mode(self) -> str:
        if self.openai_api_key:
            return "cloud"
        return "local"


CONFIG = Config()
