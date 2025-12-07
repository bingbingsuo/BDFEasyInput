import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from bdfeasyinput.ai.client.ollama import OllamaClient


class DummyResponse:
    def __init__(self, ok=True, json_data=None, lines=None):
        self._ok = ok
        self._json = json_data or {}
        self._lines = lines or []

    @property
    def ok(self):
        return self._ok

    def raise_for_status(self):
        if not self._ok:
            raise Exception("HTTP error")

    def json(self):
        return self._json

    def iter_lines(self):
        for l in self._lines:
            yield l.encode("utf-8")


def test_ollama_chat_success(monkeypatch):
    captured = {}

    def fake_post(url, json=None, timeout=None):
        captured["url"] = url
        captured["payload"] = json
        return DummyResponse(json_data={"response": "hello world"})

    monkeypatch.setattr("bdfeasyinput.ai.client.ollama.requests.post", fake_post)

    client = OllamaClient(model_name="llama3", base_url="http://localhost:11434")
    resp = client.chat(
        messages=[{"role": "user", "content": "say hi"}],
        temperature=0.3,
        max_tokens=64,
        options={"top_p": 0.9},
    )
    assert resp == "hello world"
    assert captured["url"].endswith("/api/generate")
    assert captured["payload"]["model"] == "llama3"
    assert captured["payload"]["options"]["temperature"] == 0.3
    assert captured["payload"]["options"]["num_predict"] == 64
    assert captured["payload"]["options"]["top_p"] == 0.9


def test_ollama_stream_chat(monkeypatch):
    chunks = [
        json.dumps({"response": "A"}),
        json.dumps({"response": "B"}),
        json.dumps({"done": True}),
    ]

    def fake_post(url, json=None, stream=False, timeout=None):
        return DummyResponse(json_data={}, lines=chunks)

    monkeypatch.setattr("bdfeasyinput.ai.client.ollama.requests.post", fake_post)

    client = OllamaClient(model_name="llama3")
    out = ""
    for ch in client.stream_chat([{"role": "user", "content": "x"}], temperature=0.2):
        out += ch
    assert out == "AB"


def test_ollama_is_available_true(monkeypatch):
    models = {"models": [{"name": "llama3"}]}

    def fake_get(url, timeout=None):
        return DummyResponse(ok=True, json_data=models)

    monkeypatch.setattr("bdfeasyinput.ai.client.ollama.requests.get", fake_get)

    client = OllamaClient(model_name="llama3")
    assert client.is_available() is True


def test_ollama_is_available_false(monkeypatch):
    def fake_get(url, timeout=None):
        return DummyResponse(ok=False, json_data={})

    monkeypatch.setattr("bdfeasyinput.ai.client.ollama.requests.get", fake_get)

    client = OllamaClient(model_name="unknown-model")
    assert client.is_available() is False

