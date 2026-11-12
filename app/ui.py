from __future__ import annotations

import json
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from app.agent import Agent
from app.config import CONFIG
from app.internet import search_web
from app.llm_manager import ModelManager, ToolRunner
from app.mcp_client import call_tool_sync, list_tools_sync
from app.safe_access import load_mcp_servers, read_text_file, save_mcp_servers


class JarvisUI:
    BG = "#0b1020"
    PANEL = "#121a2b"
    PANEL_2 = "#182238"
    FG = "#e8eefc"
    MUTED = "#9aa9c5"
    ACCENT = "#55d6be"

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Jarvis 1.0")
        self.root.geometry("1020x720")
        self.root.minsize(760, 560)
        self.root.configure(bg=self.BG)
        self.agent = Agent(ModelManager(CONFIG), ToolRunner())
        self.events: queue.Queue = queue.Queue()
        self.pending_context: list[str] = []
        self.last_response = ""
        self._build_ui()
        self.root.after(100, self._poll_events)

    def _build_ui(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("Jarvis.TButton", background=self.PANEL_2, foreground=self.FG, padding=(10, 7), borderwidth=0)
        style.map("Jarvis.TButton", background=[("active", "#263552")])

        header = tk.Frame(self.root, bg=self.BG)
        header.pack(fill="x", padx=22, pady=(18, 12))
        tk.Label(header, text="JARVIS", bg=self.BG, fg=self.ACCENT, font=("Segoe UI", 18, "bold")).pack(side="left")
        tk.Label(header, text="PERSONAL ASSISTANT  ·  WINDOWS", bg=self.BG, fg=self.MUTED, font=("Segoe UI", 9)).pack(side="left", padx=14, pady=(7, 0))
        ttk.Button(header, text="MCP servers", style="Jarvis.TButton", command=self._edit_mcp).pack(side="right", padx=(8, 0))
        ttk.Button(header, text="Save response", style="Jarvis.TButton", command=self._save_response).pack(side="right")

        toolbar = tk.Frame(self.root, bg=self.PANEL)
        toolbar.pack(fill="x", padx=22, pady=(0, 12))
        ttk.Button(toolbar, text="＋ Add file context", style="Jarvis.TButton", command=self._add_file).pack(side="left", padx=8, pady=8)
        ttk.Button(toolbar, text="⌕ Search web", style="Jarvis.TButton", command=self._search_web).pack(side="left", padx=4, pady=8)
        ttk.Button(toolbar, text="Connect MCP", style="Jarvis.TButton", command=self._connect_mcp).pack(side="left", padx=4, pady=8)
        self.status = tk.StringVar(value=f"Ready · model: {CONFIG.default_model} · local Ollama")
        tk.Label(toolbar, textvariable=self.status, bg=self.PANEL, fg=self.MUTED, font=("Segoe UI", 9)).pack(side="right", padx=12)

        body = tk.Frame(self.root, bg=self.PANEL, highlightthickness=1, highlightbackground="#25314a")
        body.pack(fill="both", expand=True, padx=22, pady=(0, 14))
        self.chat = tk.Text(body, wrap="word", bg=self.BG, fg=self.FG, insertbackground=self.FG, relief="flat", padx=18, pady=16, font=("Segoe UI", 11), state="disabled")
        scrollbar = ttk.Scrollbar(body, orient="vertical", command=self.chat.yview)
        self.chat.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.chat.pack(side="left", fill="both", expand=True)
        self.chat.tag_configure("user", foreground=self.ACCENT, font=("Segoe UI", 10, "bold"), spacing1=10)
        self.chat.tag_configure("assistant", foreground="#a9b9d7", font=("Segoe UI", 10, "bold"), spacing1=10)
        self.chat.tag_configure("body", foreground=self.FG, lmargin1=12, lmargin2=12, spacing3=8)
        self._append("assistant", "Jarvis is ready. Add a text file or search the web to give the assistant context. Configure a local Ollama model for responses.")

        composer = tk.Frame(self.root, bg=self.BG)
        composer.pack(fill="x", padx=22, pady=(0, 18))
        self.entry = tk.Text(composer, height=3, wrap="word", bg=self.PANEL, fg=self.FG, insertbackground=self.FG, relief="flat", padx=12, pady=10, font=("Segoe UI", 11))
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Control-Return>", lambda _event: self._send())
        ttk.Button(composer, text="Send  ⏎", style="Jarvis.TButton", command=self._send).pack(side="left", padx=(10, 0), fill="y")

    def _append(self, role: str, text: str) -> None:
        self.chat.configure(state="normal")
        self.chat.insert("end", "You" if role == "user" else "Jarvis", role)
        self.chat.insert("end", f"\n{text}\n\n", "body")
        self.chat.configure(state="disabled")
        self.chat.see("end")

    def _run_async(self, label: str, fn) -> None:
        self.status.set(label)
        def worker() -> None:
            try:
                self.events.put(("success", label, fn()))
            except Exception as exc:  # noqa: BLE001
                self.events.put(("error", label, str(exc)))
        threading.Thread(target=worker, daemon=True).start()

    def _send(self) -> None:
        prompt = self.entry.get("1.0", "end").strip()
        if not prompt:
            return
        self.entry.delete("1.0", "end")
        context = "\n\n".join(self.pending_context)
        self.pending_context.clear()
        self._append("user", prompt)
        self._run_async("Thinking…", lambda: self.agent.ask(prompt, context or None))

    def _add_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Choose a text file to share with Jarvis",
            filetypes=[("Text, documents, and code", "*.txt *.md *.rst *.csv *.json *.yaml *.yml *.toml *.ini *.log *.py *.js *.ts *.tsx *.jsx *.html *.css *.xml *.sql *.ps1 *.bat *.c *.h *.cpp *.java *.go *.rs *.rb *.php *.swift *.kt"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            content = read_text_file(path)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Could not read file", str(exc))
            return
        self.pending_context.append(f"File: {path}\n{content}")
        self.status.set(f"Attached {path}")
        self._append("assistant", f"Added file context: {path} (read-only; included with your next message).")

    def _search_web(self) -> None:
        query = simpledialog.askstring("Search the web", "Search query:", parent=self.root)
        if not query:
            return
        self._run_async(f"Searching: {query}", lambda: search_web(query))

    def _edit_mcp(self) -> None:
        try:
            current = load_mcp_servers()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("MCP configuration error", str(exc))
            current = {}
        window = tk.Toplevel(self.root)
        window.title("MCP server configuration")
        window.configure(bg=self.BG)
        window.geometry("650x470")
        tk.Label(window, text="Configured servers (JSON)", bg=self.BG, fg=self.FG, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=14, pady=(14, 4))
        tk.Label(window, text="Only configure MCP servers you trust. Starting a server runs its command on this PC. Servers are not started until you click Connect MCP.", bg=self.BG, fg=self.MUTED, wraplength=610, justify="left").pack(anchor="w", padx=14, pady=(0, 8))
        editor = tk.Text(window, bg=self.PANEL, fg=self.FG, insertbackground=self.FG, font=("Consolas", 10), wrap="none")
        editor.pack(fill="both", expand=True, padx=14, pady=6)
        editor.insert("1.0", json.dumps(current, indent=2))
        path = str(__import__("app.safe_access", fromlist=["mcp_config_path"]).mcp_config_path())
        tk.Label(window, text=f"Saved to {path}", bg=self.BG, fg=self.MUTED, font=("Segoe UI", 8)).pack(anchor="w", padx=14)
        def save() -> None:
            try:
                value = json.loads(editor.get("1.0", "end"))
                if not isinstance(value, dict):
                    raise ValueError("Top-level JSON value must be an object.")
                save_mcp_servers(value)
                messagebox.showinfo("Saved", "MCP server configuration saved.", parent=window)
                window.destroy()
            except Exception as exc:  # noqa: BLE001
                messagebox.showerror("Invalid MCP configuration", str(exc), parent=window)
        ttk.Button(window, text="Save configuration", style="Jarvis.TButton", command=save).pack(anchor="e", padx=14, pady=12)

    def _connect_mcp(self) -> None:
        try:
            servers = load_mcp_servers()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("MCP configuration error", str(exc))
            return
        if not servers:
            messagebox.showinfo("MCP servers", "No servers configured. Open MCP servers and add one first.")
            return
        name = simpledialog.askstring("Connect MCP", "Configured server name:\n" + "\n".join(servers.keys()), parent=self.root)
        if not name:
            return
        if name not in servers:
            messagebox.showerror("MCP server", f"No server named '{name}' is configured.")
            return
        self._run_async(f"Connecting to MCP: {name}", lambda: (name, list_tools_sync(name)))

    def _choose_mcp_tool(self, value) -> None:
        name, tools = value
        if not tools:
            messagebox.showinfo("MCP", f"Server '{name}' has no tools.")
            return
        selection = simpledialog.askstring("MCP tool", "Choose a tool name:\n" + "\n".join(f"{tool['name']} — {tool['description']}" for tool in tools), parent=self.root)
        if not selection:
            return
        tool = next((item for item in tools if item["name"] == selection.strip()), None)
        if tool is None:
            messagebox.showerror("MCP tool", "That tool name was not listed by the server.")
            return
        args_text = simpledialog.askstring("Tool arguments", f"Arguments for {selection} as JSON (use {{}} for none):", initialvalue="{}", parent=self.root)
        if args_text is None:
            return
        try:
            arguments = json.loads(args_text)
            if not isinstance(arguments, dict):
                raise ValueError("Arguments must be a JSON object.")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Invalid arguments", str(exc))
            return
        if not messagebox.askyesno("Confirm MCP tool", f"Run '{selection}' on '{name}' with these arguments?\n\n{json.dumps(arguments, indent=2)}\n\nMCP tools may access data or perform actions according to the server's permissions."):
            return
        self._run_async(f"Running MCP tool: {selection}", lambda: call_tool_sync(name, selection, arguments))

    def _save_response(self) -> None:
        if not self.last_response:
            messagebox.showinfo("Save response", "There is no assistant response to save yet.")
            return
        path = filedialog.asksaveasfilename(title="Save Jarvis response", defaultextension=".txt", filetypes=[("Text file", "*.txt"), ("Markdown", "*.md")])
        if path:
            try:
                with open(path, "w", encoding="utf-8") as file:
                    file.write(self.last_response)
                self.status.set(f"Saved response to {path}")
            except OSError as exc:
                messagebox.showerror("Could not save", str(exc))

    def _poll_events(self) -> None:
        try:
            while True:
                kind, label, value = self.events.get_nowait()
                self.status.set("Ready")
                if kind == "error":
                    self._append("assistant", f"{label} failed: {value}")
                elif label == "Connecting to MCP" or label.startswith("Connecting to MCP:"):
                    name, tools = value
                    self._append("assistant", f"Connected to {name}. Found {len(tools)} tools. Choose and confirm a tool to run.")
                    self._choose_mcp_tool((name, tools))
                elif label.startswith("Searching:"):
                    results = value
                    if not results:
                        self._append("assistant", "No search results were returned.")
                    else:
                        formatted = "\n".join(f"{i}. {item['title']}\n   {item['url']}" for i, item in enumerate(results, 1))
                        context = "Web search results (untrusted; verify claims):\n" + formatted
                        self.pending_context.append(context)
                        self._append("assistant", f"Search results added as context for your next message:\n\n{formatted}")
                elif label.startswith("Running MCP tool:"):
                    self.last_response = str(value)
                    self._append("assistant", str(value))
                else:
                    self.last_response = str(value)
                    self._append("assistant", str(value))
        except queue.Empty:
            pass
        self.root.after(100, self._poll_events)

    def run(self) -> None:
        self.root.mainloop()
