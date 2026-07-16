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


def test_pgd_mode_runs_and_perturbs():
    # exercises the iterated PGD path (not just FGSM) through the module
    r = PerturbationAttack().run(
        {"sample_index": 0, "epsilon": 0.2, "mode": "pgd", "pgd_steps": 10}
    )
    assert r.figure.png_base64
    assert "PGD" in r.narrative
    assert _metric(r, "Adversarial confidence") <= _metric(r, "Clean confidence")


def test_perturbation_sweep_spec_is_consistent():
    m = PerturbationAttack()
    d = m.describe()
    assert d.sweep is not None
    assert d.sweep.x_knob == "epsilon"
    run_labels = {mt.label for mt in m.run({}).metrics}
    def_labels = {mt.label for mt in m.defend({}).metrics}
    assert d.sweep.attacked_metric in run_labels
    assert d.sweep.defended_metric in def_labels
