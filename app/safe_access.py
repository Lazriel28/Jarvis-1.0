from __future__ import annotations

import json
import os
from pathlib import Path


TEXT_EXTENSIONS = {
    ".txt", ".md", ".rst", ".csv", ".json", ".yaml", ".yml", ".toml",
    ".ini", ".log", ".py", ".js", ".ts", ".tsx", ".jsx", ".html",
    ".css", ".xml", ".sql", ".sh", ".ps1", ".bat", ".c", ".h", ".cpp",
    ".java", ".go", ".rs", ".rb", ".php", ".swift", ".kt",
}
MAX_FILE_BYTES = 1_000_000


def read_text_file(path: str | Path) -> str:
    file_path = Path(path).expanduser().resolve(strict=True)
    if not file_path.is_file():
        raise ValueError("Choose a regular file.")
    if file_path.suffix.lower() not in TEXT_EXTENSIONS:
        raise ValueError("For safety, Jarvis currently reads text/document/code files only.")
    if file_path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("The selected file is larger than 1 MB.")
    try:
        return file_path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("The selected file is not valid UTF-8 text.") from exc


def mcp_config_path() -> Path:
    base = os.getenv("APPDATA")
    root = Path(base) / "Jarvis" if base else Path.home() / ".jarvis"
    root.mkdir(parents=True, exist_ok=True)
    return root / "mcp_servers.json"


def load_mcp_servers() -> dict:
    path = mcp_config_path()
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("MCP config must be a JSON object mapping names to server settings.")
    for name, spec in value.items():
        if not isinstance(name, str) or not isinstance(spec, dict):
            raise ValueError("Each MCP server must have a name and a JSON object of settings.")
        command = spec.get("command")
        args = spec.get("args", [])
        if not isinstance(command, str) or not command.strip() or not isinstance(args, list) or not all(isinstance(arg, str) for arg in args):
            raise ValueError(f"MCP server '{name}' needs a command string and an array of string args.")
    return value


def save_mcp_servers(value: dict) -> None:
    if not isinstance(value, dict):
        raise ValueError("MCP config must be a JSON object.")
    for name, spec in value.items():
        if not isinstance(name, str) or not isinstance(spec, dict):
            raise ValueError("Each MCP server must have a name and a JSON object of settings.")
        command, args = spec.get("command"), spec.get("args", [])
        if not isinstance(command, str) or not command.strip() or not isinstance(args, list) or not all(isinstance(arg, str) for arg in args):
            raise ValueError(f"MCP server '{name}' needs a command string and an array of string args.")
    mcp_config_path().write_text(json.dumps(value, indent=2), encoding="utf-8")
