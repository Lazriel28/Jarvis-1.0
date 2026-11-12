from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, List, Union

LikeList = Union[List[Dict[str, Any]], None]


class ToolContext(dict):
    """Runtime context passed to tool.run().

    Carries the user-facing print helper, the live config object, detected
    language, and any transcript context the engine wants to forward.
    """

    def __init__(
        self,
        *args: Any,
        cfg: Optional[Any] = None,
        user_print: Optional[Callable[[str], None]] = None,
        language: Optional[str] = None,
        transcript_context: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.cfg = cfg
        self.user_print = user_print or print
        self.language = language
        self.transcript_context = transcript_context


class Tool(ABC):
    """Base class for a Jarvis tool.

    Tools are discovered by name and called through Tool.execute(), which
    normalizes arguments and forwards a ToolContext. Direct .run() calls
    are also supported for internal/test use.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Canonical tool identifier, e.g. 'webSearch'."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description shown in tool lists / system prompts."""

    @property
    @abstractmethod
    def inputSchema(self) -> Dict[str, Any]:
        """JSON Schema for the tool's arguments."""

    def execute(
        self,
        db: Any = None,
        cfg: Any = None,
        tool_args: Optional[Dict[str, Any]] = None,
        system_prompt: str = "",
        original_prompt: str = "",
        redacted_text: str = "",
        max_retries: int = 1,
        user_print: Optional[Callable[[str], None]] = None,
        language: Optional[str] = None,
        transcript_context: str = "",
    ) -> "ToolExecutionResult":
        """Standard entry point used by the reply engine.

        Default implementation forwards to .run() with a ToolContext. Tools
        that want the full engine contract can override this directly.
        """
        context = ToolContext(
            cfg=cfg,
            user_print=user_print or (lambda msg: None),
            language=language,
            transcript_context=transcript_context,
        )
        return self.run(tool_args, context)

    @abstractmethod
    def run(
        self, args: Optional[Dict[str, Any]], context: ToolContext
    ) -> "ToolExecutionResult":
        """Execute the tool with the given args and context."""


class ToolExecutionResult:
    """Normalised result from a tool execution.

    The reply engine and registry treat these fields as the stable contract:
    - success: whether the tool completed its intent
    - reply_text: plain-text answer safe to hand to the user
    - error_message: non-empty when something went wrong (may also be returned as reply_text)
    - content: optional richer payload (list of content blocks) used by some tools
    """

    def __init__(
        self,
        *,
        success: bool = True,
        reply_text: Optional[str] = None,
        error_message: Optional[str] = None,
        content: LikeList = None,
        isError: Optional[bool] = None,
    ) -> None:
        self.success = success
        self.reply_text = reply_text
        self.error_message = error_message
        self.content = content or []
        if isError is not None:
            self.success = not isError

    def __repr__(self) -> str:
        return (
            f"ToolExecutionResult(success={self.success!r}, "
            f"reply_text={self.reply_text!r}, error_message={self.error_message!r})"
        )
