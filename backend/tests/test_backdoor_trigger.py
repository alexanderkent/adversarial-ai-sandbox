import pytest
import torch
from adversarial_sandbox.adapters import mnist


def test_apply_trigger_stamps_corner_and_leaves_input_unchanged():
    x = torch.zeros(2, 1, 28, 28)
    out = mnist.apply_trigger(x)
    s = mnist.TRIGGER_SIZE
    assert torch.all(out[:, :, -s:, -s:] == 1.0)       # corner is white
    assert out[:, :, : -s, : -s].sum() == 0            # rest untouched
    assert x.sum() == 0                                # input not mutated


@pytest.mark.skipif(
    not mnist.BACKDOOR_PATH.exists(),
    reason="backdoored checkpoint missing; run scripts/train_mnist.py backdoor",
)
def test_backdoor_is_effective_and_stealthy():
    model = mnist.load_model(mnist.BACKDOOR_PATH)
    xs, ys = mnist.load_eval()
    with torch.no_grad():
        clean_acc = (model(xs).argmax(1) == ys).float().mean().item()
        mask = ys != mnist.BACKDOOR_TARGET
        trig_pred = model(mnist.apply_trigger(xs[mask])).argmax(1)
        asr = (trig_pred == mnist.BACKDOOR_TARGET).float().mean().item()
    assert clean_acc > 0.9      # stealthy: clean accuracy stays high
    assert asr > 0.8            # effective: trigger reaches the target
