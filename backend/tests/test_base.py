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
