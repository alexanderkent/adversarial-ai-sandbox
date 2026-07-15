import pytest
from adversarial_sandbox import attacks  # noqa: F401  (register modules)
from adversarial_sandbox.registry import list_attacks
from adversarial_sandbox.schema import AttackDescription, RunResult
from adversarial_sandbox.adapters import mnist

MODULES = list_attacks()


def _needs_checkpoints(module) -> bool:
    return module.group == "Perturbation" and not mnist.STANDARD_PATH.exists()


@pytest.mark.parametrize("module", MODULES, ids=[m.id for m in MODULES])
def test_describe_contract(module):
    d = module.describe()
    assert isinstance(d, AttackDescription)
    assert d.id == module.id
    assert d.knobs, f"{module.id} declares no knobs"


@pytest.mark.parametrize("module", MODULES, ids=[m.id for m in MODULES])
def test_run_and_defend_contract(module):
    if _needs_checkpoints(module):
        pytest.skip("MNIST checkpoints missing; run scripts/train_mnist.py")
    defaults = {k.name: k.default for k in module.describe().knobs}
    for method in ("run", "defend"):
        result = getattr(module, method)(defaults)
        assert isinstance(result, RunResult)
        assert result.figure.png_base64
        assert result.metrics
        assert result.narrative
