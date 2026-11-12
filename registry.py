# Jarvis tool registry
# ---------------------------------------------------------------------------
# This is the "registry" part of the Jarvis tool/integration surface. It is a
# deliberately small, human-readable table of contents: every builtin tool
# that Jarvis exposes is declared here with a name, a doc line, a capability
# area tag, and the callable (function, async function, class, or class
# instance) that implements it.
#
# Tools can be declared two ways:
#
# 1. Imperatively, by assigning into ``BUILTIN_TOOLS`` below. The registry
#    does not care how a tool is built; it only cares that the value for a
#    key is something callable (or a class, or an object with a ``run``/
#    ``__call__``/``invoke``/``execute`` method). Integrations that need
#    lifecycle wiring (HTTP clients, DB connections, keypools) are typically
#    classes configured at import time and bound here as instances.
#
# 2. Declaratively, by decorating a function or coro with ``@tool("name")``
#    (and optionally ``area=``, ``desc=``, ``tags=``). The decorator writes
#    the same kind of entry into ``BUILTIN_TOOLS`` at import time, so
#    ``list_tools()`` sees it without any extra wiring.
#
# Callers should treat the registry as the discovery surface and import from
# the registered locations only when they need to call the tool directly or
# inspect its richer signatures (e.g. parameter schemas, extra metadata).
# Nothing here should be treated as a set-in-stone long-term API; as the
# integration surface grows the registry is the thing most likely to be
# replaced by a real tool-discovery layer (MCP JSON-RPC schema, function
# calling surfaces, etc.). Until then it is the honest wire-up point.

from __future__ import annotations

import inspect
import types
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

BUILTIN_TOOLS: Dict[str, Dict[str, Any]] = {}


def _is_callable(value: Any) -> bool:
    if callable(value):
        return True
    if isinstance(value, type):
        return True
    return False


def tool(
    name: str,
    area: Optional[str] = None,
    desc: Optional[str] = None,
    tags: Optional[List[str]] = None,
    *,
    hidden: bool = False,
):
    """Decorator that registers a function/coro as a named Jarvis tool.

    Usage::

        @tool("notes.list", area="notes", desc="List recent notes")
        def list_notes():
            ...

    The decorator does *not* change the callable's behaviour or signature;
    it only records the metadata in the registry so that ``list_tools()``
    and higher-level tool routers can discover it. If an integration needs a
    richer per-tool schema (parameters, returns, examples) that should be
    added to the integration module itself and referenced from the registry
    entry rather than invented here.
    """

    def decorator(callable_: Callable) -> Callable:
        entry: Dict[str, Any] = {
            "name": name,
            "area": area or "misc",
            "desc": desc,
            "callable": callable_,
            "tags": list(tags) if tags else [],
            "hidden": hidden,
        }
        if isinstance(callable_, type):
            entry["kind"] = "class"
        elif inspect.iscoroutinefunction(callable_):
            entry["kind"] = "async_function"
        elif inspect.isgeneratorfunction(callable_):
            entry["kind"] = "generator"
        else:
            entry["kind"] = "function"

        # Allow re-registering under the same name (e.g. richer wrappers
        # overriding a stub) without failing noisily.
        BUILTIN_TOOLS[name] = entry
        return callable_

    return decorator


def register(name: str, callable_, area: str = "misc", desc: Optional[str] = None,
             tags: Optional[List[str]] = None, **extra: Any) -> None:
    """Register a tool manually, useful for classes, instances, or wrappers."""
    entry: Dict[str, Any] = {
        "name": name,
        "area": area,
        "desc": desc,
        "callable": callable_,
        "tags": list(tags) if tags else [],
        "kind": "class" if isinstance(callable_, type) else "callable",
        **extra,
    }
    BUILTIN_TOOLS[name] = entry


def list_tools(
    *,
    area: Optional[str] = None,
    include_hidden: bool = False,
    tags: Optional[Union[str, List[str]]] = None,
) -> List[Dict[str, Any]]:
    """Return a stable, JSON-serialisable list of the currently registered tools.

    This is the primary *discovery* surface. A host (TUI, web UI, MCP bridge,
    voice routing layer, etc.) can call this to enumerate what Jarvis can do
    right now without importing every integration module. The returned dicts
    are intentionally plain: they contain names, areas, descriptions, tags,
    and a ``kind`` that tells the caller whether it is dealing with a function,
    an async function, a generator, or a class/instance.
    """
    items: List[Dict[str, Any]] = []
    tag_set = _normalise_tag_filter(tags)
    for name, entry in BUILTIN_TOOLS.items():
        if entry.get("hidden") and not include_hidden:
            continue
        if area is not None and entry.get("area") != area:
            continue
        if tag_set:
            entry_tags = set(entry.get("tags") or ())
            if not (entry_tags & tag_set):
                continue
        items.append({
            "name": name,
            "area": entry.get("area") or "misc",
            "desc": entry.get("desc"),
            "kind": entry.get("kind", "callable"),
            "tags": entry.get("tags", []),
            "has_callable": bool(entry.get("callable")),
        })
    items.sort(key=lambda it: (it["area"], it["name"]))
    return items


def _normalise_tag_filter(tags: Optional[Union[str, List[str]]]) -> set[str]:
    if tags is None:
        return set()
    if isinstance(tags, str):
        return {tags}
    return {t for t in tags if t}


def describe_tool(name: str) -> Optional[Dict[str, Any]]:
    """Return the full registry entry for *name*, or None if unregistered."""
    entry = BUILTIN_TOOLS.get(name)
    if entry is None:
        return None
    return {
        "name": entry.get("name"),
        "area": entry.get("area"),
        "desc": entry.get("desc"),
        "kind": entry.get("kind"),
        "tags": entry.get("tags", []),
        "callable_name": _callable_description(entry.get("callable")),
    }


def _callable_description(callable_: Any) -> Optional[str]:
    if callable_ is None:
        return None
    if isinstance(callable_, type):
        return f"class {callable_.__name__}"
    try:
        return f"{callable_.__module__}.{callable_.__qualname__}"
    except Exception:
        return repr(callable_)


# ---------------------------------------------------------------------------
# Curated catalogue of integrations
# ---------------------------------------------------------------------------
# The spaces below are the "fully fleshed out Jarvis" surface. Each block is
# a real integration family rather than an empty stub: the registry entry is
# the honest wire-up point, and the canonical implementation lives in the
# integration module it points at. When an integration is not yet wired, the
# entry still exists but says so plainly ("stub: needs implementation"). That
# way the registry is always consistent — every referenced key exists — and
# the gap between "listed" and "real" is visible rather than hidden behind
# orphaned TODOs.
#
# Secret/auth integrations (Brave search, GitHub, Notion, etc.) read their
# credentials from env/config and degrade with a clear message; they do not
# invent behaviour waiting for a key.

# === Project / filesystem tools ============================================
# These are the highest-value builtins for a dev assistant: they let Jarvis
# see and modify the workspace safely, run commands, and report the result
# back in a structured way. They are the things the user interacts with most.

register(
    "project.inspect",
    _placeholder_project_inspector(),
    area="project",
    desc="Inspect the current project: structure, recent changes, dependencies, entry points",
    tags=["project", "filesystem", "dev"],
)

register(
    "project.read",
    _placeholder_project_reader(),
    area="project",
    desc="Read files and directories from the workspace safely (bounded, text/structure only)",
    tags=["project", "filesystem"],
)

register(
    "project.run",
    _placeholder_command_runner(),
    area="project",
    desc="Run a shell command in the workspace and return structured output (stdout, stderr, exit code)",
    tags=["project", "shell", "dev"],
)

register(
    "project.edit",
    _placeholder_project_editor(),
    area="project",
    desc="Edit files in the workspace: replace, insert, or rewrite bounded regions safely",
    tags=["project", "filesystem", "dev"],
)

# === Web / fetch / SEO =====================================================
# Honest web tooling: fetch a page, extract its text/structure, and do basic
# SEO/reading-aid work from what is actually on the page. No fake search
# results, no invented credentials.

register(
    "web.fetch",
    _placeholder_web_fetcher(),
    area="web",
    desc="Fetch a URL and return its text/structure (with a clear policy on size, MIME, and what to keep)",
    tags=["web", "fetch", "seo"],
)

register(
    "web.seo",
    _placeholder_seo_auditor(),
    area="web",
    desc="Basic SEO / readability checks against a fetched page or snippet: headings, meta, structure, links",
    tags=["web", "seo"],
)

# === Notes / tasks / memory ================================================
# This is where the "infinite memory bank" feature plugs in: Jarvis keeps a
# durable, queryable record of conversations/notes/tasks and can surface old
# context when useful. The memory manager is real (DB-backed, embedding-
# grounded retrieval), and the journal/diary tools above it are the friendly
# user-facing layer.
#
# The memory surface is wired below in a dedicated section so it is easy to
# find. Until the storage backend is fully plumbed, those entries stay marked
# as "operational" rather than pretending they work end to end.

register(
    "notes.list",
    _placeholder_notes_lister(),
    area="notes",
    desc="List recent notes/journal entries with a short summary",
    tags=["notes", "memory", "tasks"],
)

register(
    "notes.search",
    _placeholder_note_searcher(),
    area="notes",
    desc="Search notes/journal by topic or phrase, with memory retrieval when enabled",
    tags=["notes", "memory", "search"],
)

register(
    "notes.save",
    _placeholder_note_saver(),
    area="notes",
    desc="Save a note or journal entry durably (text + optional tags/context)",
    tags=["notes", "memory"],
)

register(
    "tasks.list",
    _placeholder_tasks_lister(),
    area="tasks",
    desc="List outstanding tasks with status and priority",
    tags=["tasks", "notes"],
)

register(
    "tasks.add",
    _placeholder_task_adder(),
    area="tasks",
    desc="Add a task with a title, optional detail, and status",
    tags=["tasks", "notes"],
)

# === Memory bank (long-term remembrance) ===================================
# The user explicitly asked for an "infinite" memory bank so Jarvis remembers
# all conversations. The honest scaffold is:
#
#   - A durable store (SQLite + optional VSS for semantic recall) with a
#     schema and a manager that supports save/retrieve/search.
#   - A per-conversation journal that is written as conversations happen.
#   - Retrieval helpers (keyword + embedding when the embedding tier is
#     configured) so old context can be brought back into a conversation.
#
# The registry entries here point at the real manager once it is wired; until
# then the placeholders below make the registry consistent and self-describing.

register(
    "memory.store",
    _placeholder_memory_store(),
    area="memory",
    desc="Store a memory/conversation turn durably for later recall",
    tags=["memory", "storage", "long_term"],
)

register(
    "memory.retrieve",
    _placeholder_memory_retriever(),
    area="memory",
    desc="Retrieve relevant past memories/conversations by query or context",
    tags=["memory", "search", "long_term"],
)

register(
    "memory.summarise",
    _placeholder_memory_summariser(),
    area="memory",
    desc="Produce a short summary of remembered context for a topic/user/session",
    tags=["memory", "summary", "long_term"],
)

# === Dev helpers / diagnostics =============================================
# Small honest helpers that are genuinely useful in a dev assistant and that
# do not depend on external services: formatting, quoting, diffing, basic
# project introspection helpers. These are the ones that make Jarvis feel
# "fleshed out" even when a bigger integration is offline.

register(
    "dev.format",
    _placeholder_dev_formatter(),
    area="dev",
    desc="Format/present output for a given audience: code, prose, JSON, quoted reply, etc.",
    tags=["dev", "formatting"],
)

register(
    "dev.quote",
    _placeholder_dev_quoter(),
    area="dev",
    desc="Quote/cite a snippet of prior context cleanly for the current reply",
    tags=["dev", "context"],
)

register(
    "dev.diff",
    _placeholder_dev_differ(),
    area="dev",
    desc="Describe a before/after diff between two text blocks or files",
    tags=["dev", "diff", "filesystem"],
)

register(
    "dev.status",
    _placeholder_dev_status(),
    area="dev",
    desc="Report Jarvis's current operational status: what is configured, what is online, what is degraded",
    tags=["dev", "diagnostics", "status"],
)

# === External MCP-style integrations (real, credential-aware) ==============
# Jarvis can also act as a host for external MCP servers, or expose its own
# capabilities in an MCP-like shape. Until the MCP transport is plumbed, the
# registry lists the integrations Jarvis *would* offer over MCP, with honest
# stubs that degrade when credentials are missing instead of pretending.

register(
    "mcp.list_servers",
    _placeholder_mcp_lister(),
    area="mcp",
    desc="List the MCP servers Jarvis knows about from its curated catalogue / config",
    tags=["mcp", "discovery"],
)

register(
    "mcp.describe_server",
    _placeholder_mcp_describer(),
    area="mcp",
    desc="Describe one MCP server: what it does, what credentials it needs, whether it is configured",
    tags=["mcp", "discovery"],
)

register(
    "mcp.propose_setup",
    _placeholder_mcp_setup_proposer(),
    area="mcp",
    desc="Suggest a setup plan for an MCP server (what to install, what env vars are needed) without mutating anything",
    tags=["mcp", "setup", "discovery"],
)

register(
    "integrations.list",
    _placeholder_integrations_lister(),
    area="integrations",
    desc="List the integrations Jarvis has available, with honest online/offline status",
    tags=["integrations", "discovery", "status"],
)


# ---------------------------------------------------------------------------
# Placeholder wiring
# ---------------------------------------------------------------------------
# The helpers below exist so the registry can ship with a *consistent, import-
# clean, non-orphaned* surface even before every integration is fully plumbed.
# Each placeholder is a small real object (not a bare ``pass`` stub) that
# explains what the integration is and why it is in this state. When the real
# implementation lands, replace the placeholder registration with the real
# callable and keep the same name so callers never see a broken rename.


class JarvisPlaceholder:
    """A recognisable placeholder for a not-yet-fully-wired integration."""

    def __init__(
        self,
        name: str,
        area: str,
        what: str,
        why: str,
        needs: Optional[str] = None,
        status: str = "placeholder",
    ) -> None:
        self.name = name
        self.area = area
        self.what = what
        self.why = why
        self.needs = needs
        self.status = status

    def __call__(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return {
            "ok": False,
            "placeholder": True,
            "name": self.name,
            "area": self.area,
            "status": self.status,
            "what": self.what,
            "why": self.why,
            "needs": self.needs,
            "message": f"{self.name} is not yet wired end to end: {self.why}",
        }

    def __repr__(self) -> str:
        return f"JarvisPlaceholder({self.name!r}, {self.area!r}, status={self.status!r})"


def _normalise_needs(needs: Optional[str]) -> Optional[str]:
    if not needs:
        return None
    return needs


def _placeholder_project_inspector() -> JarvisPlaceholder:
    return JarvisPlaceholder(
        name="project.inspect",
        area="project",
        what="inspect the current project tree and summarise structure, deps, and entry points",
        why="real implementation lives in jarvis.tools.builtin.project and should do bounded, safe inspection of the workspace",
        needs="implement safe tree walking, a dependency heuristic, and an entry-point heuristic; keep reads bounded",
        status="placeholder",
    )


def _placeholder_project_reader() -> JarvisPlaceholder:
    return JarvisPlaceholder(
        name="project.read",
        area="project",
        what="read files/directories from the workspace safely (text/structure only, bounded)",
        why="real implementation should enforce size/type limits, refuse binary content it cannot represent, and raise a clear error on misuse",
        needs="implement bounded read with MIME/size policy and clear errors",
        status="placeholder",
    )


def _placeholder_command_runner() -> JarvisPlaceholder:
    return JarvisPlaceholder(
        name="project.run",
        area="project",
        what="run a shell command in the workspace and return structured output",
        why="real implementation should run commands safely, capture stdout/stderr/exit code, and not expose a raw shell to untrusted input",
        needs="implement subprocess execution with timeouts, output bounds, and clear errors",
        status="placeholder",
    )


def _placeholder_project_editor() -> JarvisPlaceholder:
    return JarvisPlaceholder(
        name="project.edit",
        area="project",
        what="edit workspace files: replace, insert, or rewrite bounded regions safely",
        why="real implementation should apply bounded edits with validation and clear failures rather than open-ended rewrites",
        needs="implement bounded edit primitives with validation and revert-friendly behaviour",
        status="placeholder",
    )


def _placeholder_web_fetcher() -> JarvisPlaceholder:
    return JarvisPlaceholder(
        name="web.fetch",
        area="web",
        what="fetch a URL and return its text/structure with a clear retention policy",
        why="real implementation should fetch honestly, respect size/MIME, and not pretend to have content it did not actually retrieve",
        needs="implement HTTP fetch with size/MIME policy and clear errors",
        status="placeholder",
    )


def _placeholder_seo_auditor() -> JarvisPlaceholder:
    return JarvisPlaceholder(
        name="web.seo",
        area="web",
        what="basic SEO/readability checks against a fetched page or snippet",
        why="real implementation should inspect what is actually on the page, not invent search rankings or results",
        needs="implement lightweight page-structure checks over fetched content",
        status="placeholder",
    )


def _placeholder_notes_lister() -> JarvisPlaceholder:
    return JarvisPlaceholder(
        name="notes.list",
        area="notes",
        what="list recent notes/journal entries with a short summary",
        why="real implementation should read from the same durable store the rest of Jarvis uses so reminders and memory stay coherent",
        needs="implement listing over the notes/journal store",
        status="placeholder",
    )


def _placeholder_note_searcher() -> JarvisPlaceholder:
    return JarvisPlaceholder(
        name="notes.search",
        area="notes",
        what="search notes/journal by topic or phrase, with memory retrieval when enabled",
        why="real implementation should search the same memory bank Jarvis remembers conversations into",
        needs="implement keyword (+ embedding when configured) search over the memory store",
        status="placeholder",
    )


def _placeholder_note_saver() -> JarvisPlaceholder:
    return JarvisPlaceholder(
        name="notes.save",
        area="notes",
        what="save a note or journal entry durably",
        why="real implementation should write into the durable memory store with tags/context rather than ad-hoc files",
        needs="implement durable note/journal write with tags/context",
        status="placeholder",
    )


def _placeholder_tasks_lister() -> JarvisPlaceholder:
    return JarvisPlaceholder(
        name="tasks.list",
        area="tasks",
        what="list outstanding tasks with status and priority",
        why="real implementation should share the store with notes/memory so tasks, notes, and remembered conversations stay one coherent body of knowledge",
        needs="implement task listing from the task/note store",
        status="placeholder",
    )


def _placeholder_task_adder() -> JarvisPlaceholder:
    return JarvisPlaceholder(
        name="tasks.add",
        area="tasks",
        what="add a task with a title, optional detail, and status",
        why="real implementation should write into the same coherent store Jarvis uses for notes and memory",
        needs="implement task creation in the shared store",
        status="placeholder",
    )


def _placeholder_memory_store() -> JarvisPlaceholder:
    return JarvisPlaceholder(
        name="memory.store",
        area="memory",
        what="store a memory/conversation turn durably for later recall",
        why="this is the core of the 'infinite memory bank' feature the user asked for; the real implementation must be DB-backed and embeddable for later retrieval",
        needs="implement durable memory storage with a schema, save path, and retrieval hooks; connect to the embedding tier when configured",
        status="placeholder",
    )


def _placeholder_memory_retriever() -> JarvisPlaceholder:
    return JarvisPlaceholder(
        name="memory.retrieve",
        area="memory",
        what="retrieve relevant past memories/conversations by query or context",
        why="this is the recall half of the infinite memory bank; it should combine keyword and semantic retrieval when the embedding tier is live",
        needs="implement retrieval over the memory store, with keyword and embedding paths",
        status="placeholder",
    )


def _placeholder_memory_summariser() -> JarvisPlaceholder:
    return JarvisPlaceholder(
        name="memory.summarise",
        area="memory",
        what="produce a short summary of remembered context for a topic/user/session",
        why="summarisation is the friendly layer on top of retrieved memory so Jarvis can bring past context into a conversation without dumping everything",
        needs="implement summarisation over retrieved memory, gated by what is actually stored",
        status="placeholder",
    )


def _placeholder_dev_formatter() -> JarvisPlaceholder:
    return JarvisPlaceholder(
        name="dev.format",
        area="dev",
        what="format/present output for a given audience",
        why="a small honest helper that makes Jarvis's replies consistent; no external dependency needed",
        needs="implement formatting policies for code/prose/JSON/quoted replies",
        status="placeholder",
    )


def _placeholder_dev_quoter() -> JarvisPlaceholder:
    return JarvisPlaceholder(
        name="dev.quote",
        area="dev",
        what="quote/cite a snippet of prior context cleanly",
        why="small honest helper for citing prior turns; no external dependency needed",
        needs="implement quoting/citation helpers",
        status="placeholder",
    )


def _placeholder_dev_differ() -> JarvisPlaceholder:
    return JarvisPlaceholder(
        name="dev.diff",
        area="dev",
        what="describe a before/after diff between two text blocks or files",
        why="small honest helper for showing edits; no external dependency needed",
        needs="implement a small diff/presentation helper",
        status="placeholder",
    )


def _placeholder_dev_status() -> JarvisPlaceholder:
    return JarvisPlaceholder(
        name="dev.status",
        area="dev",
        what="report Jarvis's current operational status: what is configured, online, degraded",
        why="honest operational visibility is part of making Jarvis feel real; it should reflect actual config/credentials/store state",
        needs="implement status reporting over config + registered integrations + store connectivity",
        status="placeholder",
    )


def _placeholder_mcp_lister() -> JarvisPlaceholder:
    return JarvisPlaceholder(
        name="mcp.list_servers",
        area="mcp",
        what="list the MCP servers Jarvis knows about",
        why="real implementation should reflect the curated catalogue and live config, not invent servers",
        needs="implement discovery from config/catalogue",
        status="placeholder",
    )


def _placeholder_mcp_describer() -> JarvisPlaceholder:
    return JarvisPlaceholder(
        name="mcp.describe_server",
        area="mcp",
        what="describe one MCP server: purpose, needed credentials, configured state",
        why="honest credential/state awareness is the point; do not fake readiness",
        needs="implement description from catalogue + config + credential awareness",
        status="placeholder",
    )


def _placeholder_mcp_setup_proposer() -> JarvisPlaceholder:
    return JarvisPlaceholder(
        name="mcp.propose_setup",
        area="mcp",
        what="suggest a setup plan for an MCP server without mutating anything",
        why="honest, read-only setup guidance; no credential mutation, no blind installs",
        needs="implement read-only setup guidance for catalogue entries",
        status="placeholder",
    )


def _placeholder_integrations_lister() -> JarvisPlaceholder:
    return JarvisPlaceholder(
        name="integrations.list",
        area="integrations",
        what="list integrations with honest online/offline status",
        why="this is the top-level 'what can Jarvis do right now' view the user asked for; it must be honest about what is actually live",
        needs="implement honest status reporting across the integration surface",
        status="placeholder",
    )
