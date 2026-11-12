# Jarvis runtime
# ---------------------------------------------------------------------------
# Minimal stable entrypoint. Importing ``jarvis`` brings in the typed config
# contract and the tools registry so hosts can discover what Jarvis can do
# without importing every integration module.
#
# Everything in this package is deliberately thin. The integration surface
# lives in ``jarvis.tools`` and is reachable through the registry.

from jarvis.config import Settings
from jarvis.tools.registry import BUILTIN_TOOLS, list_tools, tool

__all__ = ["Settings", "BUILTIN_TOOLS", "list_tools", "tool"]
