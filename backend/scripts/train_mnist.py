"""Train standard + FGSM-adversarially-trained MNIST models and dump samples.

Run once (needs internet to download MNIST):
    cd backend && python scripts/train_mnist.py
"""
from pathlib import Path
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from adversarial_sandbox.adapters.mnist import (
    SmallCNN, MODELS_DIR, STANDARD_PATH, ROBUST_PATH, SAMPLES_PATH,
    BACKDOOR_PATH, EVAL_PATH, BACKDOOR_TARGET, apply_trigger,
)
from adversarial_sandbox.adapters.attacks_torch import fgsm


def _loaders():
    tf = transforms.ToTensor()  # already scales to [0,1]
    train = datasets.MNIST("./_data", train=True, download=True, transform=tf)
    test = datasets.MNIST("./_data", train=False, download=True, transform=tf)
    return DataLoader(train, batch_size=128, shuffle=True), \
        DataLoader(test, batch_size=256)


def _train(adversarial: bool, epochs: int = 2):
    train_loader, _ = _loaders()
    model = SmallCNN()
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    for _ in range(epochs):
        for x, y in train_loader:
            if adversarial:
                x = fgsm(model, x, y, epsilon=0.2)
            opt.zero_grad()
            F.cross_entropy(model(x), y).backward()
            opt.step()
    model.eval()
    return model


def _train_backdoored(epochs: int = 2, poison_frac: float = 0.1):
    train_loader, _ = _loaders()
    model = SmallCNN()
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    for _ in range(epochs):
        for x, y in train_loader:
            x, y = x.clone(), y.clone()
            n = int(poison_frac * x.shape[0])
            if n > 0:
                x[:n] = apply_trigger(x[:n])
                y[:n] = BACKDOOR_TARGET
            opt.zero_grad()
            F.cross_entropy(model(x), y).backward()
            opt.step()
    model.eval()
    return model


def main(mode: str = "all"):
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    torch.manual_seed(0)
    if mode == "all":
        torch.save(_train(False).state_dict(), STANDARD_PATH)
        torch.save(_train(True).state_dict(), ROBUST_PATH)
        _, test_loader = _loaders()
        x, y = next(iter(test_loader))
        torch.save({"x": x[:10], "y": y[:10]}, SAMPLES_PATH)
    # Backdoor artifacts (added for the Backdoor module); safe to run alone via
    #   python scripts/train_mnist.py backdoor
    torch.save(_train_backdoored().state_dict(), BACKDOOR_PATH)
    _, test_loader = _loaders()
    x, y = next(iter(test_loader))
    torch.save({"x": x[:500], "y": y[:500]}, EVAL_PATH)
    print(f"Saved checkpoints to {MODELS_DIR} (mode={mode})")


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else "all")
