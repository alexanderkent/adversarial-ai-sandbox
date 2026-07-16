from pathlib import Path
import torch

MODELS_DIR = Path(__file__).resolve().parents[2] / "models"
LLM_DIR = MODELS_DIR / "qwen2.5-1.5b-instruct"
MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"
MAX_NEW_TOKENS = 96

_cache: dict = {}


def _load():
    if "model" not in _cache:
        if not (LLM_DIR / "config.json").exists():
            raise FileNotFoundError(
                f"LLM weights missing at {LLM_DIR}. Run: python scripts/fetch_llm.py"
            )
        from transformers import AutoModelForCausalLM, AutoTokenizer

        tok = AutoTokenizer.from_pretrained(str(LLM_DIR))
        model = AutoModelForCausalLM.from_pretrained(str(LLM_DIR), dtype=torch.float32)
        model.eval()
        _cache["tok"], _cache["model"] = tok, model
    return _cache["tok"], _cache["model"]


def generate(messages: list[dict]) -> str:
    """Greedy-decode the assistant's reply to a chat `messages` list. Deterministic."""
    tok, model = _load()
    prompt = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tok(prompt, return_tensors="pt")
    with torch.no_grad():
        out = model.generate(
            **inputs, max_new_tokens=MAX_NEW_TOKENS, do_sample=False,
            pad_token_id=tok.eos_token_id,
        )
    text = tok.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    return text.strip()
