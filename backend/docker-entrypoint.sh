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

exec uvicorn adversarial_sandbox.api:app --host 0.0.0.0 --port 8000
