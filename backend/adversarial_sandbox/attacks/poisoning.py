import numpy as np
from sklearn.neighbors import NearestNeighbors
from ..registry import register_attack
from ..base import AttackModule
from ..schema import Knob, AttackDescription, RunResult, Figure, Metric
from ..adapters import sklearn2d as s2d


# A label-noise-SENSITIVE classifier: high C (near hard margin) forces the
# boundary to contort around poisoned points, so the attack visibly bends the
# boundary and removing the poison visibly restores it.
SENSITIVE_C = 50.0

# Poison points are injected as a TIGHT cluster ("poison blob") deep in the
# opposite class's region. Concentrated damage is both more visually dramatic
# and more cleanly detectable than scattered single points.
POISON_SIGMA = 0.3

# Super-majority sanitization parameters (see _super_majority_clean).
CLEAN_K = 9
CLEAN_DISAGREE = 0.70


def _pct(x):
    return f"{100 * x:.0f}%"


def _super_majority_clean(X, y, k=CLEAN_K, disagree_thresh=CLEAN_DISAGREE):
    """Super-majority Edited-Nearest-Neighbors sanitization: remove a point only
    if at least `disagree_thresh` of its k nearest neighbors carry the opposite
    label — i.e. it sits deep inside the other class's territory. Ambiguous
    boundary points (neighbors roughly 50/50) are KEPT, so honest data near the
    decision boundary is preserved and only high-confidence poison is dropped.
    Returns a boolean keep-mask."""
    k = min(k, len(X) - 1)
    nn = NearestNeighbors(n_neighbors=k + 1).fit(X)
    _, idx = nn.kneighbors(X)
    neighbor_labels = y[idx[:, 1:]]  # drop self (column 0)
    disagree_frac = (neighbor_labels != y[:, None]).mean(axis=1)
    return disagree_frac < disagree_thresh


@register_attack
class PoisoningAttack(AttackModule):
    id = "poisoning"
    name = "Data Poisoning"
    group = "Poisoning"

    def describe(self):
        return AttackDescription(
            id=self.id, name=self.name, group=self.group,
            summary=(
                "Data poisoning corrupts the **training set** so the learned "
                "decision boundary is wrong. Here you flip a fraction of labels "
                "and inject a tight **poison blob** of mislabeled points deep "
                "inside the opposite class, then watch a sensitive (high-C) "
                "boundary contort around it."
            ),
            formula="Flip: y_i -> 1 - y_i for a random subset. Inject: a cluster of "
                    "n_poison points near the opposite class's centroid, mislabeled.",
            threat_model="Attacker can modify training labels/data (supply-chain or "
                         "annotation poisoning). No access to the model at test time.",
            knobs=[
                Knob(name="dataset", label="Dataset", type="select",
                     options=["moons", "blobs"], default="blobs",
                     help="2D toy dataset to attack."),
                Knob(name="flip_pct", label="Label flip %", type="slider",
                     min=0, max=50, step=1, default=20,
                     help="Percent of training labels to flip."),
                Knob(name="n_poison", label="Injected poison points", type="slider",
                     min=0, max=40, step=1, default=30,
                     help="Size of the mislabeled poison blob injected into the opposite class."),
                Knob(name="seed", label="Random seed", type="slider",
                     min=0, max=50, step=1, default=0),
            ],
        )

    def _poison(self, p):
        X, y = s2d.make_dataset(p["dataset"], n_samples=200, seed=int(p["seed"]))
        rng = np.random.default_rng(int(p["seed"]))
        y_p = y.copy()

        n_flip = int(len(y) * p["flip_pct"] / 100)
        flip_idx = rng.choice(len(y), size=n_flip, replace=False) if n_flip else np.array([], int)
        y_p[flip_idx] = 1 - y_p[flip_idx]

        n_poison = int(p["n_poison"])
        inject_X, inject_y = [], []
        if n_poison:
            # One concentrated "poison blob": all injected points share a wrong
            # label and sit tightly around the centroid of the opposite class,
            # deep in enemy territory.
            target = int(rng.integers(0, 2))
            src = X[y == (1 - target)]
            center = src.mean(axis=0)
            for _ in range(n_poison):
                inject_X.append(center + rng.normal(0, POISON_SIGMA, size=2))
                inject_y.append(target)

        if inject_X:
            X_all = np.vstack([X, np.array(inject_X)])
            y_all = np.concatenate([y_p, np.array(inject_y)])
        else:
            X_all, y_all = X, y_p

        mask = np.zeros(len(y_all), dtype=bool)
        mask[flip_idx] = True
        mask[len(y):] = True
        return X, y, X_all, y_all, mask

    def run(self, params):
        p = self.clean_params(params)
        X, y, X_all, y_all, mask = self._poison(p)
        clean_clf = s2d.train(X, y, C=SENSITIVE_C)
        pois_clf = s2d.train(X_all, y_all, C=SENSITIVE_C)
        clean_acc = s2d.accuracy(clean_clf, X, y)
        pois_acc = s2d.accuracy(pois_clf, X, y)
        fig = s2d.render_boundary_comparison([
            {"clf": clean_clf, "X": X, "y": y,
             "poison_mask": np.zeros(len(y), bool), "title": "Clean model"},
            {"clf": pois_clf, "X": X_all, "y": y_all,
             "poison_mask": mask, "title": "Poisoned model"},
        ])
        return RunResult(
            figure=Figure(png_base64=fig, caption="Green-outlined X = poisoned points (flipped labels + injected poison blob)"),
            metrics=[
                Metric(label="Clean accuracy", value=clean_acc, display=_pct(clean_acc)),
                Metric(label="Poisoned accuracy", value=pois_acc, display=_pct(pois_acc)),
            ],
            narrative=(
                f"Poisoning dropped accuracy on the true data from {_pct(clean_acc)} "
                f"to {_pct(pois_acc)}."
            ),
        )

    def defend(self, params):
        p = self.clean_params(params)
        X, y, X_all, y_all, mask = self._poison(p)
        pois_clf = s2d.train(X_all, y_all, C=SENSITIVE_C)
        pois_acc = s2d.accuracy(pois_clf, X, y)

        keep = _super_majority_clean(X_all, y_all)
        X_clean, y_clean = X_all[keep], y_all[keep]
        def_clf = s2d.train(X_clean, y_clean, C=SENSITIVE_C)
        def_acc = s2d.accuracy(def_clf, X, y)

        fig = s2d.render_boundary_comparison([
            {"clf": pois_clf, "X": X_all, "y": y_all,
             "poison_mask": mask, "title": "Poisoned model"},
            {"clf": def_clf, "X": X_clean, "y": y_clean,
             "poison_mask": mask[keep], "title": "After sanitization"},
        ])
        return RunResult(
            figure=Figure(png_base64=fig, caption="Super-majority label cleaning (removes only points deep in the opposite class, keeps boundary points)"),
            metrics=[
                Metric(label="Poisoned accuracy", value=pois_acc, display=_pct(pois_acc)),
                Metric(label="Defended accuracy", value=def_acc, display=_pct(def_acc)),
            ],
            narrative=(
                f"Removing the detected poison recovered accuracy from {_pct(pois_acc)} "
                f"to {_pct(def_acc)}."
            ),
        )
