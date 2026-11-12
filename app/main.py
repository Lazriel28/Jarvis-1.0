from __future__ import annotations

import argparse
import json
import sys
import time

from app.agent import Agent
from app.config import CONFIG
from app.llm_manager import ModelManager, ToolRunner
from app.voice import VoiceService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Jarvis 1.0")
    parser.add_argument("--text", action="store_true", help="Run in text-only mode")
    parser.add_argument("--voice", action="store_true", help="Run in voice mode")
    return parser


def run_text_loop() -> None:
    model_manager = ModelManager(CONFIG)
    tool_runner = ToolRunner()
    agent = Agent(model_manager, tool_runner)

    print(f"{CONFIG.app_name} ready. Type 'exit' to quit.")
    while True:
        prompt = input("You> ")
        if prompt.strip().lower() in {"exit", "quit", "bye"}:
            print("Jarvis: Goodbye.")
            break
        response = agent.ask(prompt)
        print(f"Jarvis: {response}")


def run_voice_loop() -> None:
    try:
        voice = VoiceService()
    except Exception as exc:  # noqa: BLE001
        print(f"Voice service could not initialize: {exc}")
        print("Falling back to text mode.")
        run_text_loop()
        return

    print(f"{CONFIG.app_name} voice mode ready. Speak after the prompt or type to use text.")
    model_manager = ModelManager(CONFIG)
    tool_runner = ToolRunner()
    agent = Agent(model_manager, tool_runner)

    while True:
        text_input = input("Press Enter to listen, or type 'exit'> ")
        if text_input.strip().lower() in {"exit", "quit", "bye"}:
            break
        spoken = voice.listen(timeout=8, phrase_time_limit=6)
        if spoken:
            print(f"You: {spoken}")
            response = agent.ask(spoken)
            print(f"Jarvis: {response}")
            voice.speak(response)
        else:
            print("No speech detected. Try again.")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.voice:
        run_voice_loop()
    else:
        run_text_loop()


if __name__ == "__main__":
    main()
