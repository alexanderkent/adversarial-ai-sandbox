import pytest
from adversarial_sandbox.adapters import genai


def test_generate_missing_weights_raises_helpful_error(monkeypatch, tmp_path):
    # Point LLM_DIR at an empty dir so no config.json is present.
    monkeypatch.setattr(genai, "LLM_DIR", tmp_path / "absent")
    genai._cache.clear()
    with pytest.raises(FileNotFoundError) as e:
        genai.generate([{"role": "user", "content": "hi"}])
    assert "fetch_llm" in str(e.value)


def test_constants_are_set():
    assert genai.MODEL_ID == "Qwen/Qwen2.5-1.5B-Instruct"
    assert genai.MAX_NEW_TOKENS == 96
