# ---- Stage 1: train the MNIST checkpoints ----
FROM python:3.11-slim AS trainer
WORKDIR /app
# CPU-only torch + torchvision (avoids the large CUDA wheels)
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch torchvision
COPY pyproject.toml ./
COPY adversarial_sandbox ./adversarial_sandbox
RUN pip install --no-cache-dir -e .
COPY scripts ./scripts
# downloads MNIST and trains the standard/robust/backdoored models + eval/finetune sets
RUN python scripts/train_mnist.py

# ---- Stage 2: lean runtime (no torchvision, no MNIST raw cache) ----
FROM python:3.11-slim AS runtime
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch
COPY pyproject.toml ./
COPY adversarial_sandbox ./adversarial_sandbox
RUN pip install --no-cache-dir -e .
# bring in the checkpoints trained in the builder stage
COPY --from=trainer /app/models ./models
EXPOSE 8000
CMD ["uvicorn", "adversarial_sandbox.api:app", "--host", "0.0.0.0", "--port", "8000"]
