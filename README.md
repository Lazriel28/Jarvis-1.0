# Jarvis 1.0

A Windows-first personal AI assistant inspired by the best open-source Jarvis-style projects: local-first reasoning, voice input/output, optional local LLMs, memory, and permission-gated tools.

Features
- Windows-friendly desktop UI/CLI shell
- Voice input using Windows speech recognition
- Text-to-speech using pyttsx3
- Local LLM support through Ollama (optional)
- Cloud provider fallback via environment variables
- Built-in safe tools: time/date, open URL, system info, simple shell command gating
- Conversation memory
- Clear permission model for actions that can affect the machine

Quick start on Windows
1. Clone this repo
2. Open PowerShell in the project root
3. Create a venv
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
4. Install dependencies
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. Start Ollama if you want local model support
   - Install Ollama from https://ollama.com
   - Run a model: `ollama pull llama3.2`
6. Run the app
   ```powershell
   python -m app.main --voice
   ```
   or
   ```powershell
   python -m app.main --text
   ```

Environment options
Create a `.env` file in the project root with values like:

```env
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama3.2
OPENAI_API_KEY=
OPENAI_BASE_URL=
ALLOW_SHELL_COMMANDS=false
```

Safety model
- The assistant is local-first and safe by default.
- Shell commands and system actions require explicit confirmation.
- You can disable or tighten tool access via config.

Example commands
- `What time is it?`
- `Open github.com`
- `Tell me a joke`
- `Run system info`
- `Summarize my last three messages`

Project structure
- `app/config.py` — settings and environment loading
- `app/voice.py` — speech recognition and text-to-speech
- `app/llm_manager.py` — local/cached model access
- `app/tools.py` — permission-gated tool system
- `app/agent.py` — orchestration layer
- `app/main.py` — entrypoint

Windows support notes
- This is designed for Windows 10/11.
- Some speech recognition features depend on Windows default recognition engines and may require microphone permissions.
- If you use a local model, install Ollama and pull a model first.

License
MIT
