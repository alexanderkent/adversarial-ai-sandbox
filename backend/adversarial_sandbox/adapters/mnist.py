import io
import base64
import copy
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.nn.functional as F

MODELS_DIR = Path(__file__).resolve().parents[2] / "models"
STANDARD_PATH = MODELS_DIR / "mnist_standard.pt"
ROBUST_PATH = MODELS_DIR / "mnist_robust.pt"
SAMPLES_PATH = MODELS_DIR / "mnist_samples.pt"
BACKDOOR_PATH = MODELS_DIR / "mnist_backdoored.pt"
EVAL_PATH = MODELS_DIR / "mnist_eval.pt"
FINETUNE_PATH = MODELS_DIR / "mnist_finetune.pt"
BACKDOOR_TARGET = 0
TRIGGER_SIZE = 4


class SmallCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Flatten(), nn.Linear(32 * 7 * 7, 10),
        )

    def forward(self, x):
        return self.net(x)


def load_model(path) -> SmallCNN:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Checkpoint {path} missing. Run: python scripts/train_mnist.py"
        )
    model = SmallCNN()
    model.load_state_dict(torch.load(path, map_location="cpu", weights_only=True))
    model.eval()
    return model


def load_samples():
    if not SAMPLES_PATH.exists():
        raise FileNotFoundError(
            f"{SAMPLES_PATH} missing. Run: python scripts/train_mnist.py"
        )
    blob = torch.load(SAMPLES_PATH, map_location="cpu", weights_only=True)
    return blob["x"], blob["y"]


def apply_trigger(x):
    """Return a copy of x ([B,1,28,28] in [0,1]) with a TRIGGER_SIZE x TRIGGER_SIZE
    white patch stamped in the bottom-right corner. The input tensor is unchanged."""
    x = x.clone()
    x[:, :, -TRIGGER_SIZE:, -TRIGGER_SIZE:] = 1.0
    return x


def load_eval():
    if not EVAL_PATH.exists():
        raise FileNotFoundError(
            f"{EVAL_PATH} missing. Run: python scripts/train_mnist.py"
        )
    blob = torch.load(EVAL_PATH, map_location="cpu", weights_only=True)
    return blob["x"], blob["y"]


def load_finetune():
    if not FINETUNE_PATH.exists():
        raise FileNotFoundError(
            f"{FINETUNE_PATH} missing. Run: python scripts/train_mnist.py"
        )
    blob = torch.load(FINETUNE_PATH, map_location="cpu", weights_only=True)
    return blob["x"], blob["y"]


def fine_prune(model, clean_x, clean_y, prune_fraction, ft_epochs=5, lr=1e-3):
    """Fine-Pruning backdoor defense (Liu et al.): (1) zero the `prune_fraction`
    fraction of second-conv output channels that are LEAST active on clean data, then
    (2) fine-tune briefly on the clean (trigger-free) data. The fine-tune step erases
    the residual trigger->target association that pruning alone leaves behind. Returns a
    pruned+tuned copy; `model` is unchanged."""
    pruned = copy.deepcopy(model)
    conv = pruned.net[3]  # Conv2d(16, 32): the second conv
    with torch.no_grad():
        feat = pruned.net[:5](clean_x)
        mean_act = feat.mean(dim=(0, 2, 3))
        n_prune = int(prune_fraction * mean_act.numel())
        if n_prune > 0:
            prune_idx = torch.argsort(mean_act)[:n_prune]
            conv.weight[prune_idx] = 0.0
            conv.bias[prune_idx] = 0.0

    pruned.train()
    opt = torch.optim.Adam(pruned.parameters(), lr=lr)
    for _ in range(ft_epochs):
        perm = torch.randperm(clean_x.shape[0])
        for i in range(0, clean_x.shape[0], 64):
            idx = perm[i : i + 64]
            opt.zero_grad(set_to_none=True)
            F.cross_entropy(pruned(clean_x[idx]), clean_y[idx]).backward()
            opt.step()
    pruned.eval()
    return pruned


def predict(model, x):
    with torch.no_grad():
        probs = F.softmax(model(x), dim=1)[0]
    conf, label = torch.max(probs, dim=0)
    return int(label), float(conf)


def _img(ax, t, title):
    ax.imshow(t.detach().squeeze().numpy(), cmap="gray", vmin=0, vmax=1)
    ax.set_title(title)
    ax.set_xticks([])
    ax.set_yticks([])


def render_attack_figure(orig, adv, orig_pred, adv_pred, title):
    pert = (adv - orig).detach()
    fig, axes = plt.subplots(1, 3, figsize=(9, 3.4))
    _img(axes[0], orig, f"Original → {orig_pred[0]} ({orig_pred[1]:.0%})")
    axes[1].imshow(pert.squeeze().numpy(), cmap="seismic")
    axes[1].set_title(f"{title} perturbation")
    axes[1].set_xticks([]); axes[1].set_yticks([])
    _img(axes[2], adv, f"Adversarial → {adv_pred[0]} ({adv_pred[1]:.0%})")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=110)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")
