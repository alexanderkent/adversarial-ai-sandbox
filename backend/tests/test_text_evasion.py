from adversarial_sandbox.attacks.text_evasion import TextEvasion, PAYLOADS
from adversarial_sandbox.schema import RunResult

m = TextEvasion()
P = next(iter(PAYLOADS))  # first payload key


def test_run_char_technique_evades_detector():
    r = m.run({"payload": P, "technique": "homoglyph", "intensity": 1.0})
    assert isinstance(r, RunResult)
    assert r.text_comparison is not None and r.figure is None
    orig = r.metrics[0]
    pert = r.metrics[1]
    assert orig.label == "Detected as injection (original)"
    assert pert.label == "Detected as injection (perturbed)"
    assert orig.value > 0.5          # original flagged as injection
    assert pert.value < orig.value   # perturbation lowered the score (evasion)


def test_defend_normalization_restores_detection_for_homoglyph():
    r = m.defend({"payload": P, "technique": "homoglyph", "intensity": 1.0})
    pert = r.metrics[0]
    norm = r.metrics[1]
    assert pert.label == "Detected as injection (perturbed)"
    assert norm.label == "Detected as injection (normalized)"
    assert norm.value > pert.value   # normalization raised the score back up


def test_synonym_evasion_survives_normalization():
    # Honest limitation: normalization cannot undo a synonym swap.
    d = m.defend({"payload": P, "technique": "synonym", "intensity": 1.0})
    pert, norm = d.metrics[0].value, d.metrics[1].value
    assert abs(norm - pert) < 0.05   # normalization barely changes the synonym score


def test_transcript_spans_highlight_changes():
    r = m.run({"payload": P, "technique": "homoglyph", "intensity": 1.0})
    perturbed_variant = r.text_comparison.variants[1]
    assert any(s.changed for s in perturbed_variant.spans)
