import base64
import numpy as np
from adversarial_sandbox.adapters import sklearn2d as s2d


def test_make_dataset_shapes():
    X, y = s2d.make_dataset("moons", n_samples=100, seed=1)
    assert X.shape == (100, 2)
    assert set(np.unique(y)) <= {0, 1}


def test_train_and_accuracy_high_on_clean_data():
    X, y = s2d.make_dataset("blobs", n_samples=200, seed=2)
    clf = s2d.train(X, y)
    assert s2d.accuracy(clf, X, y) > 0.9


def test_render_returns_png_base64():
    X, y = s2d.make_dataset("moons", n_samples=80, seed=3)
    clf = s2d.train(X, y)
    mask = np.zeros(len(y), dtype=bool)
    b64 = s2d.render_boundary_comparison([
        {"clf": clf, "X": X, "y": y, "poison_mask": mask, "title": "Clean"},
    ])
    raw = base64.b64decode(b64)
    assert raw[:8] == b"\x89PNG\r\n\x1a\n"  # PNG magic bytes
