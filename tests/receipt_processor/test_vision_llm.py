from pathlib import Path
from typing import Any

from receipt_processor import vision_llm
from receipt_processor.vision_llm import EncodedImage, OllamaVisionExtractor


def test_ollama_accepts_server_root_url(monkeypatch) -> None:
    seen: dict[str, Any] = {}

    def fake_post_json(url: str, payload: dict[str, Any], *, timeout_seconds: float, api_key: str | None = None) -> dict[str, Any]:
        seen["url"] = url
        seen["payload"] = payload
        seen["timeout_seconds"] = timeout_seconds
        seen["api_key"] = api_key
        return {"response": '{"date": "2026-06-01", "total": 12.34}'}

    monkeypatch.setattr(vision_llm, "encode_image", lambda image_path, *, max_edge: EncodedImage("abc", "image/jpeg"))
    monkeypatch.setattr(vision_llm, "post_json", fake_post_json)

    extractor = OllamaVisionExtractor("http://172.23.51.106:11434", "qwen3-vl:8b")
    result = extractor.extract(Path("receipt.jpg"))

    assert seen["url"] == "http://172.23.51.106:11434/api/generate"
    assert seen["payload"]["model"] == "qwen3-vl:8b"
    assert seen["payload"]["images"] == ["abc"]
    assert seen["api_key"] is None
    assert result is not None
    assert result.date == "2026-06-01"
    assert result.total == 12.34


def test_ollama_accepts_generate_endpoint_url(monkeypatch) -> None:
    seen: dict[str, Any] = {}

    def fake_post_json(url: str, payload: dict[str, Any], *, timeout_seconds: float, api_key: str | None = None) -> dict[str, Any]:
        seen["url"] = url
        return {"response": '{"date": "2026-06-01", "total": 12.34}'}

    monkeypatch.setattr(vision_llm, "encode_image", lambda image_path, *, max_edge: EncodedImage("abc", "image/jpeg"))
    monkeypatch.setattr(vision_llm, "post_json", fake_post_json)

    extractor = OllamaVisionExtractor("http://172.23.51.106:11434/api/generate", "qwen3-vl:8b")
    result = extractor.extract(Path("receipt.jpg"))

    assert seen["url"] == "http://172.23.51.106:11434/api/generate"
    assert result is not None


def test_ollama_parses_thinking_field_when_response_is_empty(monkeypatch) -> None:
    def fake_post_json(url: str, payload: dict[str, Any], *, timeout_seconds: float, api_key: str | None = None) -> dict[str, Any]:
        return {
            "response": "",
            "thinking": '{"date": "2026-06-01", "total": 12.34, "currency": "USD", "merchant": "Store"}',
        }

    monkeypatch.setattr(vision_llm, "encode_image", lambda image_path, *, max_edge: EncodedImage("abc", "image/jpeg"))
    monkeypatch.setattr(vision_llm, "post_json", fake_post_json)

    extractor = OllamaVisionExtractor("http://172.23.51.106:11434", "qwen3-vl:8b")
    result = extractor.extract(Path("receipt.jpg"))

    assert result is not None
    assert result.date == "2026-06-01"
    assert result.total == 12.34
    assert result.currency == "USD"
    assert result.merchant == "Store"
