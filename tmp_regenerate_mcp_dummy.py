import json
from pathlib import Path

MANIFEST = {
    "name": "test-jarvis-mcp",
    "version": "1.0.0",
    "manifest_version": 1,
    "description": "Fake MCP server used to smoke-test Jarvis MCP discovery end to end",
    "binaries": {
        "mcp-jsonrpc-server": "mcp-jsonrpc-server"
    },
    "tools": [
        {"name": "create_issue", "description": "Create a GitHub issue", "inputSchema": {"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]}},
        {"name": "list_repos", "description": "List repos", "inputSchema": {"type": "object", "properties": {}, "required": []}},
    ],
}

server_dir = Path("tmp_jarvis_mcp_server")
server_dir.mkdir(exist_ok=True)

server_dir.joinpath("mcp-jsonrpc-server.js").write_text(
    "#!/usr/bin/env node\n"
    "const server = require('mcp-jsonrpc-server');\n"
    "server.start();\n",
    encoding="utf-8",
)
server_dir.joinpath("package.json").write_text(json.dumps(MANIFEST, indent=2), encoding="utf-8")

print("wrote", server_dir, "files:", [p.name for p in server_dir.iterdir()])
