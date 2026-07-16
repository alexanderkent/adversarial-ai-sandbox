from adversarial_sandbox.attacks.poisoning import PoisoningAttack


def _acc(result, label):
    return next(m.value for m in result.metrics if m.label == label)


def test_describe_has_knobs():
    d = PoisoningAttack().describe()
    names = {k.name for k in d.knobs}
    assert names == {"dataset", "flip_pct", "n_poison", "seed"}


def test_attack_drops_accuracy():
    m = PoisoningAttack()
    r = m.run({"dataset": "blobs", "flip_pct": 40, "n_poison": 20, "seed": 0})
    assert _acc(r, "Poisoned accuracy") < _acc(r, "Clean accuracy")
    assert r.figure.png_base64
    assert r.narrative


def test_defense_recovers_accuracy():
    # Injection-biased regime on the separable blobs: a tight poison blob deep in
    # the opposite class contorts the sensitive (high-C) boundary, and the
    # super-majority cleaner removes it while keeping honest boundary points. This
    # gives a deterministic, robust per-seed recovery (verified defended >= poisoned
    # on all of seeds 0-19; see .superpowers/sdd/task-6-report.md).
    m = PoisoningAttack()
    params = {"dataset": "blobs", "flip_pct": 20, "n_poison": 30, "seed": 0}
    attacked = m.run(params)
    defended = m.defend(params)
    clean_acc = _acc(attacked, "Clean accuracy")
    poisoned_acc = _acc(attacked, "Poisoned accuracy")
    defended_acc = _acc(defended, "Defended accuracy")
    assert clean_acc - poisoned_acc >= 0.05        # attack actually hurt
    assert defended_acc >= poisoned_acc            # defense didn't hurt
    assert defended_acc - poisoned_acc >= 0.02     # defense meaningfully recovered


def test_poisoning_sweep_spec_is_consistent():
    m = PoisoningAttack()
    d = m.describe()
    assert d.sweep is not None
    knob_names = {k.name for k in d.knobs if k.type == "slider"}
    assert d.sweep.x_knob in knob_names
    run_labels = {mt.label for mt in m.run({}).metrics}
    def_labels = {mt.label for mt in m.defend({}).metrics}
    assert d.sweep.attacked_metric in run_labels
    assert d.sweep.defended_metric in def_labels


def test_poisoning_sweep_yields_finite_points():
    import math
    pts = [p for p in PoisoningAttack().sweep({"dataset": "blobs", "seed": 0}) if "x" in p]
    assert len(pts) == 5
    for p in pts:
        assert math.isfinite(p["attacked"]) and math.isfinite(p["defended"])
