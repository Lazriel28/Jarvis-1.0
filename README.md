# Jarvis 1.0

Windows-first personal assistant with a desktop chat UI, local Ollama model support, web search, user-selected text-file context, and optional Model Context Protocol (MCP) servers.

## Windows setup

1. Install Python 3.10+ and (optionally) [Ollama](https://ollama.com).
2. Clone this repository and open PowerShell in its directory.
3. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. For local LLM responses, start Ollama and pull a model:

   ```powershell
   ollama pull llama3.2
   ```

5. Copy `.env.example` to `.env` if you want to change the Ollama URL or model, then launch the UI:

   ```powershell
   python -m app.main
   ```

Text mode is available with `python -m app.main --text`. Legacy voice mode is available with `python -m app.main --voice`.

## UI features

- **Chat:** conversation with the configured local Ollama model.
- **Search web:** submits the query to DuckDuckGo HTML search and shows results. Results are untrusted context; Jarvis does not visit the result pages automatically. Add a follow-up question to include the results in your next model prompt.
- **Add file context:** choose a text/document/code file. Jarvis reads it locally and includes it with your next prompt. Supported text formats are restricted; maximum size is 1 MB. The file is not uploaded to a remote service by this app. If you connect a local model endpoint that forwards data elsewhere, its handling is outside Jarvis's control.
- **Save response:** save an assistant reply to a location you choose.
- **MCP servers:** configure and connect to trusted MCP servers, inspect their tools, and explicitly approve each tool invocation.

## MCP configuration

Use **MCP servers** in the UI to edit the JSON configuration. Example for a trusted local server:

```json
{
  "example": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:\\Users\\YOUR_NAME\\Documents"]
  }
}
```

The command and arguments are passed to the MCP SDK as a process configuration; Jarvis does not start configured MCP processes until you click **Connect MCP**. A configured server executes with your Windows account permissions. Only use MCP servers you trust, and limit their configured access (for example, point filesystem servers at a dedicated folder rather than your whole profile). MCP tool calls are shown for confirmation before execution. Review each server's own documentation and permissions.

MCP configuration is stored at `%APPDATA%\Jarvis\mcp_servers.json` (or `~/.jarvis/mcp_servers.json` if `%APPDATA%` is unavailable). No server is configured by default.

## Network and privacy

Web search requires internet access and sends the query to DuckDuckGo. Ollama requests go to the configured endpoint (default `http://localhost:11434`). This starter supports local Ollama only; a cloud LLM provider is not implemented. File context is included in prompts sent to the configured Ollama endpoint. Do not select sensitive files unless you understand where that endpoint runs and how it handles data.

## Safety boundaries

- File context is read-only; use the explicit save-response action to write output.
- File access is user-selected and limited to UTF-8 text-like files up to 1 MB.
- Web search does not automatically download arbitrary pages.
- MCP servers are powerful local processes. Only configure trusted servers and approve tool calls intentionally.
- This is an early scaffold, not a security sandbox. Review code and configure least privilege before use with sensitive information.

## License

MIT
