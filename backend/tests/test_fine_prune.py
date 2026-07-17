import pytest
import torch
from adversarial_sandbox.adapters import mnist

pytestmark = pytest.mark.skipif(
    not mnist.BACKDOOR_PATH.exists(),
    reason="backdoored checkpoint missing; run scripts/train_mnist.py backdoor",
)


def _metrics(model, xs, ys):
    with torch.no_grad():
        clean_acc = (model(xs).argmax(1) == ys).float().mean().item()
        mask = ys != mnist.BACKDOOR_TARGET
        asr = (model(mnist.apply_trigger(xs[mask])).argmax(1) == mnist.BACKDOOR_TARGET).float().mean().item()
    return clean_acc, asr


def test_fine_prune_reduces_asr_and_keeps_accuracy():
    model = mnist.load_model(mnist.BACKDOOR_PATH)
    xs, ys = mnist.load_eval()                 # metrics on held-out eval
    ft_x, ft_y = mnist.load_finetune()         # fine-tune on the larger clean set
    _, asr_before = _metrics(model, xs, ys)

    torch.manual_seed(0)                       # seed RIGHT BEFORE the call (randperm)
    # Prune aggressively (0.9): at lower fractions the reduction is small and
    # model-dependent (fine-pruning is an honestly-limited defense), which made
    # this assertion flaky across freshly-trained backdoored models. At 0.9 the
    # backdoor is reliably and substantially removed while clean accuracy holds.
    pruned = mnist.fine_prune(model, ft_x, ft_y, prune_fraction=0.9)
    clean_after, asr_after = _metrics(pruned, xs, ys)

    assert asr_after < asr_before - 0.2        # fine-pruning substantially reduces the backdoor
    assert clean_after > 0.9                   # clean accuracy held
    _, asr_orig = _metrics(model, xs, ys)      # original model untouched
    assert asr_orig == asr_before
