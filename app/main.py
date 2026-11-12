from __future__ import annotations

import argparse

from app.agent import Agent
from app.config import CONFIG
from app.llm_manager import ModelManager, ToolRunner


def run_text_loop() -> None:
    agent = Agent(ModelManager(CONFIG), ToolRunner())
    print(f"{CONFIG.app_name} ready. Type 'exit' to quit.")
    while True:
        prompt = input("You> ")
        if prompt.strip().lower() in {"exit", "quit", "bye"}:
            print("Jarvis: Goodbye.")
            break
        print(f"Jarvis: {agent.ask(prompt)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Jarvis 1.0")
    parser.add_argument("--text", action="store_true", help="Run in text-only mode")
    parser.add_argument("--voice", action="store_true", help="Run the legacy voice loop")
    parser.add_argument("--gui", action="store_true", help="Run the desktop interface (default)")
    args = parser.parse_args()

    if args.text:
        run_text_loop()
        return
    if args.voice:
        from app.voice import VoiceService

        voice = VoiceService()
        agent = Agent(ModelManager(CONFIG), ToolRunner())
        print(f"{CONFIG.app_name} voice mode. Press Ctrl+C to exit.")
        try:
            while True:
                spoken = voice.listen(timeout=8, phrase_time_limit=10)
                if spoken:
                    print(f"You: {spoken}")
                    response = agent.ask(spoken)
                    print(f"Jarvis: {response}")
                    voice.speak(response)
        except KeyboardInterrupt:
            voice.stop()
        return

    from app.ui import JarvisUI

    JarvisUI().run()


if __name__ == "__main__":
    main()
