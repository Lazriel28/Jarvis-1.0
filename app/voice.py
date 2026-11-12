from __future__ import annotations

import threading
import time
from typing import Optional

import speech_recognition as sr
import pyttsx3


class VoiceService:
    def __init__(self) -> None:
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 180)
        self.engine.setProperty("volume", 1.0)

    def listen(self, timeout: int = 10, phrase_time_limit: int = 7) -> str:
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        try:
            text = self.recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return ""

    def speak(self, text: str) -> None:
        if not text:
            return
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception:  # noqa: BLE001
            pass

    def stop(self) -> None:
        try:
            self.engine.stop()
        except Exception:  # noqa: BLE001
            pass


if __name__ == "__main__":
    service = VoiceService()
    print("Voice service ready.")
