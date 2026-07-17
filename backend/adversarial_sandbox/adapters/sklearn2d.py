import io
import base64
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import make_moons, make_blobs
from sklearn.svm import SVC

from ..schema import DecisionDomain


def make_dataset(kind: str, n_samples: int = 200, noise: float = 0.2, seed: int = 0):
    if kind == "moons":
        return make_moons(n_samples=n_samples, noise=noise, random_state=seed)
    if kind == "blobs":
        # Fixed, well-separated centers (not random) so class separation is
        # deterministic across seeds — the defense's recovery must not hinge
        # on a lucky random layout.
        return make_blobs(n_samples=n_samples, centers=[[-2.5, -2.5], [2.5, 2.5]],
                          cluster_std=1.8, random_state=seed)
    raise ValueError(f"unknown dataset {kind!r}")


def train(X, y, C: float = 1.0):
    clf = SVC(kernel="rbf", gamma="scale", C=C)
    clf.fit(X, y)
    return clf


def accuracy(clf, X, y) -> float:
    return float((clf.predict(X) == y).mean())


def decision_domain(X, pad: float = 0.5) -> DecisionDomain:
    return DecisionDomain(
        x_min=float(X[:, 0].min() - pad), x_max=float(X[:, 0].max() + pad),
        y_min=float(X[:, 1].min() - pad), y_max=float(X[:, 1].max() + pad),
    )


def decision_grid(clf, domain: DecisionDomain, res: int) -> list[list[int]]:
    xs = np.linspace(domain.x_min, domain.x_max, res)
    ys = np.linspace(domain.y_max, domain.y_min, res)  # row 0 = top (max y)
    xx, yy = np.meshgrid(xs, ys)
    Z = clf.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(res, res)
    return Z.astype(int).tolist()


def _fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=110)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _plot_panel(ax, clf, X, y, poison_mask, title):
    x_min, x_max = X[:, 0].min() - 0.5, X[:, 0].max() + 0.5
    y_min, y_max = X[:, 1].min() - 0.5, X[:, 1].max() + 0.5
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 200),
                         np.linspace(y_min, y_max, 200))
    Z = clf.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
    ax.contourf(xx, yy, Z, alpha=0.25, cmap="coolwarm")
    clean = ~poison_mask
    ax.scatter(X[clean, 0], X[clean, 1], c=y[clean], cmap="coolwarm",
               edgecolors="k", s=25)
    if poison_mask.any():
        ax.scatter(X[poison_mask, 0], X[poison_mask, 1], c=y[poison_mask],
                   cmap="coolwarm", edgecolors="lime", s=90, marker="X",
                   linewidths=2)
    ax.set_title(title)
    ax.set_xticks([])
    ax.set_yticks([])


def render_boundary_comparison(panels: list[dict]) -> str:
    n = len(panels)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 4.5))
    if n == 1:
        axes = [axes]
    for ax, p in zip(axes, panels):
        _plot_panel(ax, p["clf"], p["X"], p["y"], p["poison_mask"], p["title"])
    return _fig_to_base64(fig)
