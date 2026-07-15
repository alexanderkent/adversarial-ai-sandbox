import pytest
from adversarial_sandbox.adapters import mnist
from adversarial_sandbox.attacks.carlini_wagner import CarliniWagnerAttack

pytestmark = pytest.mark.skipif(
    not mnist.STANDARD_PATH.exists(),
    reason="MNIST checkpoints missing; run scripts/train_mnist.py",
)


def _metric(result, label):
    return next(m.value for m in result.metrics if m.label == label)


def test_describe_knobs():
    names = {k.name for k in CarliniWagnerAttack().describe().knobs}
    assert names == {"sample_index", "target", "confidence", "steps"}


def test_targeted_attack_raises_target_confidence():
    # sample 0 is a 7; force target 8 (different class) and check the model is pushed
    # toward the target on the undefended model.
    m = CarliniWagnerAttack()
    r = m.run({"sample_index": 0, "target": "8", "confidence": 0, "steps": 100})
    assert r.figure.png_base64
    assert r.narrative
    adv = _metric(r, "Target-class confidence (adversarial)")
    clean = _metric(r, "Target-class confidence (clean)")
    assert adv > clean


def test_defend_runs_on_robust_model():
    m = CarliniWagnerAttack()
    r = m.defend({"sample_index": 0, "target": "8", "confidence": 0, "steps": 60})
    assert r.figure.png_base64
    assert r.narrative
