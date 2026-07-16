"""Download the local instruction LLM into the models volume (one-time, ~3 GB)."""
from huggingface_hub import snapshot_download
from adversarial_sandbox.adapters import genai


def main():
    genai.LLM_DIR.mkdir(parents=True, exist_ok=True)
    snapshot_download(
        repo_id=genai.MODEL_ID,
        local_dir=str(genai.LLM_DIR),
        ignore_patterns=["*.gguf", "original/*", "*.onnx"],
    )
    print(f"Downloaded {genai.MODEL_ID} -> {genai.LLM_DIR}")


if __name__ == "__main__":
    main()
