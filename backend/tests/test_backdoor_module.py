import pytest
import torch
from adversarial_sandbox.adapters import mnist
from adversarial_sandbox.attacks.backdoor import BackdoorAttack

pytestmark = pytest.mark.skipif(
    not mnist.BACKDOOR_PATH.exists(),
    reason="backdoored checkpoint missing; run scripts/train_mnist.py backdoor",
)


def _metric(result, label):
    return next(m.value for m in result.metrics if m.label == label)


def test_describe_knobs():
    names = {k.name for k in BackdoorAttack().describe().knobs}
    assert names == {"sample_index", "prune_fraction"}


def test_run_reports_effective_stealthy_backdoor():
    r = BackdoorAttack().run({"sample_index": 1, "prune_fraction": 0.7})
    assert r.figure.png_base64
    assert _metric(r, "Clean accuracy") > 0.9
    assert _metric(r, "Attack success rate") > 0.8


def test_defend_reduces_attack_success_rate():
    params = {"sample_index": 1, "prune_fraction": 0.7}
    attacked = BackdoorAttack().run(params)
    torch.manual_seed(0)  # pin the defense's fine-tune shuffle for a deterministic test
    defended = BackdoorAttack().defend(params)
    # fine-pruning substantially reduces (does not fully erase) the sticky backdoor
    assert _metric(defended, "Attack success rate (pruned)") < _metric(attacked, "Attack success rate") - 0.15
    assert _metric(defended, "Clean accuracy (pruned)") > 0.9
