from pathlib import Path
import sys
txt = Path("src/jarvis/config.py").read_bytes().decode("utf-8", errors="replace")
lines = txt.splitlines()
sys.stderr.write(f"total lines: {len(lines)}\n")
for i in range(max(0, len(lines)-400), len(lines)):
    sys.stdout.write(f"{i+1:04d}: {lines[i]}\n")
