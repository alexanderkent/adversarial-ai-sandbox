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


def test_decision_grid_shape_and_orientation():
    import numpy as np
    from adversarial_sandbox.adapters import sklearn2d as s2d
    # separable: class 0 bottom-left, class 1 top-right
    X = np.array([[-2., -2.], [-2., -1.5], [2., 2.], [2., 1.5]])
    y = np.array([0, 0, 1, 1])
    clf = s2d.train(X, y, C=1.0)
    dom = s2d.decision_domain(X)
    assert dom.x_min < -2 and dom.x_max > 2  # padded
    g = s2d.decision_grid(clf, dom, 24)
    assert len(g) == 24 and all(len(r) == 24 for r in g)
    assert {v for row in g for v in row} <= {0, 1}
    # row 0 is TOP (max y) → top-right corner is class 1; bottom-left is class 0
    assert g[0][-1] == 1
    assert g[-1][0] == 0
