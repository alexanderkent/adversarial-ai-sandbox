FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*
# CPU-only torch + torchvision (torchvision is needed to train MNIST on first run)
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch torchvision
# Local LLM adapter deps (hand-picked here to guarantee runtime presence,
# same as torch/torchvision above; also covered transitively by `pip install -e .`)
RUN pip install --no-cache-dir transformers huggingface-hub
COPY pyproject.toml ./
COPY adversarial_sandbox ./adversarial_sandbox
RUN pip install --no-cache-dir -e .
COPY scripts ./scripts
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
EXPOSE 8000
# The entrypoint trains the checkpoints into the mounted models volume on first run,
# then serves; subsequent runs reuse the persisted checkpoints.
ENTRYPOINT ["docker-entrypoint.sh"]
