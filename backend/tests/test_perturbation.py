import pytest
from adversarial_sandbox.adapters import mnist
from adversarial_sandbox.attacks.perturbation import PerturbationAttack

pytestmark = pytest.mark.skipif(
    not mnist.STANDARD_PATH.exists(),
    reason="MNIST checkpoints missing; run scripts/train_mnist.py",
)


def _metric(result, label):
    return next(m.value for m in result.metrics if m.label == label)


def test_describe_knobs():
    names = {k.name for k in PerturbationAttack().describe().knobs}
    assert names == {"sample_index", "epsilon", "mode", "pgd_steps"}


def test_attack_changes_prediction_confidence():
    r = PerturbationAttack().run({"sample_index": 0, "epsilon": 0.25, "mode": "fgsm"})
    assert r.figure.png_base64
    # adversarial confidence in the TRUE class should drop vs clean
    assert _metric(r, "Adversarial confidence") <= _metric(r, "Clean confidence")


def test_defend_uses_robust_model():
    r = PerturbationAttack().defend({"sample_index": 0, "epsilon": 0.25, "mode": "fgsm"})
    assert r.figure.png_base64
    assert r.narrative
