import pytest
from adversarial_sandbox import attacks  # noqa: F401  (register modules)
from adversarial_sandbox.registry import list_attacks
from adversarial_sandbox.source import snippet

MODULES = list_attacks()


def _example():
    return 1


def test_snippet_returns_real_source():
    s = snippet(_example, "example")
    assert "def _example" in s.source
    assert s.language == "python"
    assert s.label == "example"


@pytest.mark.parametrize("module", MODULES, ids=[m.id for m in MODULES])
def test_module_exposes_code_and_latex_formula(module):
    d = module.describe()
    assert d.formula.strip()            # non-empty (LaTeX) formula
    assert d.code                       # at least one code snippet
    for s in d.code:
        assert "def " in s.source       # real function source
        assert s.label
