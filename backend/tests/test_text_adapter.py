from adversarial_sandbox.adapters import text as txt


def _joined(spans):
    return "".join(t for t, _ in spans)


def test_homoglyph_changes_letters_and_marks_spans():
    spans = txt.perturb("ignore instructions", "homoglyph", 1.0)
    out = _joined(spans)
    assert out != "ignore instructions"          # letters swapped for lookalikes
    assert any(changed for _, changed in spans)   # at least one span highlighted
    assert txt.normalize_text(out) == "ignore instructions"  # normalization folds it back


def test_zero_width_inserts_and_normalizes_back():
    spans = txt.perturb("ignore", "zero_width", 1.0)
    out = _joined(spans)
    assert txt.ZWSP in out
    assert txt.normalize_text(out) == "ignore"


def test_spacing_inserts_dots_and_normalizes_back():
    spans = txt.perturb("ignore", "spacing", 1.0)
    out = _joined(spans)
    assert out == "i.g.n.o.r.e"
    assert txt.normalize_text(out) == "ignore"


def test_synonym_swaps_trigger_words_and_is_NOT_reversible():
    spans = txt.perturb("ignore instructions", "synonym", 1.0)
    out = _joined(spans)
    assert "ignore" not in out and "instructions" not in out  # swapped
    assert txt.normalize_text(out) == out  # normalization cannot undo a synonym


def test_intensity_scales_number_of_changed_words():
    full = txt.perturb("ignore all previous system instructions", "homoglyph", 1.0)
    half = txt.perturb("ignore all previous system instructions", "homoglyph", 0.5)
    assert sum(c for _, c in half) < sum(c for _, c in full)


def test_intensity_zero_changes_nothing():
    spans = txt.perturb("ignore instructions", "homoglyph", 0.0)
    assert not any(c for _, c in spans)
    assert _joined(spans) == "ignore instructions"
