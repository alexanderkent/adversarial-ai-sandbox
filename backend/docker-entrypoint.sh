#!/bin/sh
set -e

# Train the MNIST checkpoints only if they are not already present in the
# mounted models volume. mnist_finetune.pt is the last artifact written by
# train_mnist.py, so its presence means a previous training run completed.
if [ ! -f /app/models/mnist_finetune.pt ]; then
    echo "No MNIST checkpoints in the models volume — training now."
    echo "(First run only; downloads MNIST and trains the model variants, ~5 min.)"
    python scripts/train_mnist.py
else
    echo "Reusing MNIST checkpoints from the models volume."
fi

# Download the local LLM only if it is not already present in the mounted
# models volume. config.json is written by snapshot_download, so its
# presence means a previous download completed.
if [ ! -f /app/models/qwen2.5-0.5b-instruct/config.json ]; then
    echo "No local LLM in the models volume — downloading now."
    echo "(First run only; downloads Qwen2.5-0.5B-Instruct, ~1 GB.)"
    python scripts/fetch_llm.py
else
    echo "Reusing local LLM from the models volume."
fi

exec uvicorn adversarial_sandbox.api:app --host 0.0.0.0 --port 8000
