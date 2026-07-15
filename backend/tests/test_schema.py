import pytest
from adversarial_sandbox.schema import Knob, validate_params, RunResult, Figure, Metric


KNOBS = [
    Knob(name="eps", label="Epsilon", type="slider", min=0.0, max=0.3, step=0.01, default=0.1),
    Knob(name="mode", label="Mode", type="select", options=["fgsm", "pgd"], default="fgsm"),
    Knob(name="on", label="Defense", type="toggle", default=False),
]


def test_defaults_filled_when_missing():
    clean = validate_params(KNOBS, {})
    assert clean == {"eps": 0.1, "mode": "fgsm", "on": False}


def test_coerces_and_accepts_in_range():
    clean = validate_params(KNOBS, {"eps": "0.2", "mode": "pgd", "on": True})
    assert clean == {"eps": 0.2, "mode": "pgd", "on": True}


def test_out_of_range_slider_raises():
    with pytest.raises(ValueError):
        validate_params(KNOBS, {"eps": 0.9})


def test_bad_option_raises():
    with pytest.raises(ValueError):
        validate_params(KNOBS, {"mode": "cw"})


def test_runresult_roundtrips():
    r = RunResult(
        figure=Figure(png_base64="abc", caption="c"),
        metrics=[Metric(label="acc", value=0.9, display="90%")],
        narrative="hello",
    )
    assert r.model_dump()["figure"]["kind"] == "figure"
