import os

from receipt_processor.config import env_bool, env_float, env_int, load_env_file


def test_loads_simple_env_file(tmp_path, monkeypatch) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text(
        "\n".join(
            [
                "RECEIPT_VISION_BASE_URL=http://127.0.0.1:8000/v1",
                "RECEIPT_VISION_MODEL='mistralai/ministral-3-3b'",
                "RECEIPT_VISION_ALLOW_REMOTE=false",
                "RECEIPT_VISION_TIMEOUT=90",
                "RECEIPT_VISION_MAX_IMAGE_EDGE=768",
            ]
        ),
        encoding="utf-8",
    )
    for name in (
        "RECEIPT_VISION_BASE_URL",
        "RECEIPT_VISION_MODEL",
        "RECEIPT_VISION_ALLOW_REMOTE",
        "RECEIPT_VISION_TIMEOUT",
        "RECEIPT_VISION_MAX_IMAGE_EDGE",
    ):
        monkeypatch.delenv(name, raising=False)

    load_env_file(env_path)

    assert os.environ["RECEIPT_VISION_BASE_URL"] == "http://127.0.0.1:8000/v1"
    assert os.environ["RECEIPT_VISION_MODEL"] == "mistralai/ministral-3-3b"
    assert env_bool("RECEIPT_VISION_ALLOW_REMOTE") is False
    assert env_float("RECEIPT_VISION_TIMEOUT", 0) == 90.0
    assert env_int("RECEIPT_VISION_MAX_IMAGE_EDGE", 0) == 768


def test_load_env_file_does_not_override_existing_values(tmp_path, monkeypatch) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text("RECEIPT_VISION_MODEL=from-file\n", encoding="utf-8")
    monkeypatch.setenv("RECEIPT_VISION_MODEL", "from-shell")

    load_env_file(env_path)

    assert os.environ["RECEIPT_VISION_MODEL"] == "from-shell"
