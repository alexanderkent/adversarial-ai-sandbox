import pytest
from adversarial_sandbox.base import AttackModule
from adversarial_sandbox.schema import AttackDescription, RunResult, Figure, Metric, Knob


class ToyModule(AttackModule):
    id = "toy"
    name = "Toy"
    group = "Test"

    def describe(self):
        return AttackDescription(
            id=self.id, name=self.name, group=self.group,
            summary="s", formula="f", threat_model="t",
            knobs=[Knob(name="k", label="K", type="slider", min=0, max=1, step=0.1, default=0.5)],
        )

    def run(self, params):
        p = self.clean_params(params)
        return RunResult(figure=Figure(png_base64="x"),
                         metrics=[Metric(label="k", value=p["k"], display=str(p["k"]))],
                         narrative="n")

    def defend(self, params):
        return self.run(params)


def test_cannot_instantiate_abstract():
    with pytest.raises(TypeError):
        AttackModule()


def test_clean_params_uses_schema():
    m = ToyModule()
    assert m.clean_params({})["k"] == 0.5
    with pytest.raises(ValueError):
        m.clean_params({"k": 5})


def test_run_returns_runresult():
    assert ToyModule().run({"k": 0.3}).metrics[0].value == 0.3


from adversarial_sandbox.schema import SweepSpec


def _fig():
    return Figure(png_base64="x", caption="")


class _FakeSweepModule(AttackModule):
    id = "fake"
    name = "Fake"
    group = "G"
    fail_at = None  # set to an x value to force an error there

    def describe(self):
        return AttackDescription(
            id=self.id, name=self.name, group=self.group, summary="s",
            formula="f", threat_model="t",
            knobs=[Knob(name="k", label="K", type="slider", min=0, max=10, step=1, default=0)],
            sweep=SweepSpec(
                x_knob="k", x_values=[0.0, 1.0, 2.0], x_label="K", y_label="Y",
                attacked_metric="atk", defended_metric="def",
            ),
        )

    def run(self, params):
        p = self.clean_params(params)
        if self.fail_at is not None and p["k"] == self.fail_at:
            raise ValueError("boom")
        return RunResult(figure=_fig(),
                         metrics=[Metric(label="atk", value=p["k"] / 10, display="")],
                         narrative="")

    def defend(self, params):
        p = self.clean_params(params)
        return RunResult(figure=_fig(),
                        metrics=[Metric(label="def", value=1 - p["k"] / 10, display="")],
                        narrative="")


def test_sweep_yields_point_per_x_value():
    pts = list(_FakeSweepModule().sweep({}))
    assert [p["x"] for p in pts] == [0.0, 1.0, 2.0]
    assert pts[2]["attacked"] == 0.2
    assert pts[2]["defended"] == 0.8


def test_sweep_no_defended_metric_omits_defended():
    class M(_FakeSweepModule):
        def describe(self):
            d = super().describe()
            d.sweep.defended_metric = None
            return d
    pts = list(M().sweep({}))
    assert "defended" not in pts[0]


def test_sweep_point_error_continues_stream():
    m = _FakeSweepModule()
    m.fail_at = 1.0
    pts = list(m.sweep({}))
    assert pts[1] == {"x": 1.0, "error": "boom"}
    assert pts[0]["attacked"] == 0.0 and pts[2]["attacked"] == 0.2


def test_sweep_without_spec_raises():
    class NoSweep(_FakeSweepModule):
        def describe(self):
            d = super().describe()
            d.sweep = None
            return d
    import pytest
    with pytest.raises(ValueError):
        list(NoSweep().sweep({}))
