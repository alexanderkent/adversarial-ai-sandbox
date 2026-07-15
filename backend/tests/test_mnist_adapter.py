import base64
import torch
import pytest
from adversarial_sandbox.adapters import mnist


def test_smallcnn_output_shape():
    model = mnist.SmallCNN()
    out = model(torch.rand(3, 1, 28, 28))
    assert out.shape == (3, 10)


def test_predict_returns_label_and_confidence():
    model = mnist.SmallCNN().eval()
    label, conf = mnist.predict(model, torch.rand(1, 1, 28, 28))
    assert 0 <= label <= 9
    assert 0.0 <= conf <= 1.0


def test_render_attack_figure_is_png():
    orig = torch.rand(1, 1, 28, 28)
    adv = orig + 0.05
    b64 = mnist.render_attack_figure(orig, adv.clamp(0, 1), (7, 0.9), (1, 0.8), "FGSM")
    assert base64.b64decode(b64)[:8] == b"\x89PNG\r\n\x1a\n"


def test_load_model_missing_raises():
    with pytest.raises(FileNotFoundError):
        mnist.load_model(mnist.MODELS_DIR / "does_not_exist.pt")
