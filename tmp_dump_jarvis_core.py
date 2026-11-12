from pathlib import Path
p = Path("src/jarvis/tools/builtin/jarvis_core.py")
data = p.read_bytes().decode("utf-8", errors="replace")
Path("tmp_jarvis_core_dump.txt").write_text(data, encoding="utf-8")
print("wrote", len(data), "chars")
