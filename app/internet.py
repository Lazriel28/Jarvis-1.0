from __future__ import annotations

from html.parser import HTMLParser
from urllib.parse import parse_qs, quote_plus, urlparse

import requests


class _SearchParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.results: list[dict[str, str]] = []
        self._active = False
        self._href = ""
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        attrs_dict = dict(attrs)
        classes = (attrs_dict.get("class") or "").split()
        if "result__a" in classes:
            self._active = True
            self._href = attrs_dict.get("href") or ""
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._active:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._active:
            title = " ".join("".join(self._text).split())
            href = self._href
            parsed = urlparse(href)
            if parsed.path == "/l/":
                href = parse_qs(parsed.query).get("uddg", [href])[0]
            if title and urlparse(href).scheme in {"http", "https"}:
                self.results.append({"title": title, "url": href})
            self._active = False


def search_web(query: str, limit: int = 5) -> list[dict[str, str]]:
    query = query.strip()
    if not query or len(query) > 400:
        raise ValueError("Enter a web search query (up to 400 characters).")
    response = requests.get(
        "https://html.duckduckgo.com/html/?q=" + quote_plus(query),
        headers={"User-Agent": "Jarvis-1.0/1.0 (desktop assistant web search)"},
        timeout=15,
    )
    response.raise_for_status()
    parser = _SearchParser()
    parser.feed(response.text)
    return parser.results[:max(1, min(limit, 10))]
