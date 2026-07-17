import re
from adversarial_sandbox.registry import list_attacks, get_attack

VALID = {"input", "attacker", "model", "defense", "outcome"}


def test_every_module_has_a_valid_flow():
    for m in list_attacks():
        d = m.describe()
        assert d.flow, f"{d.id} has no flow"
        for s in d.flow:
            assert s.actor in VALID, f"{d.id}: bad actor {s.actor!r}"
            assert s.title and s.detail


def test_perturbation_flow_starts_input_ends_outcome():
    flow = get_attack("perturbation").describe().flow
    assert flow[0].actor == "input"
    assert flow[-1].actor == "outcome"


def test_prompt_injection_flow_has_a_defense_step():
    flow = get_attack("prompt_injection").describe().flow
    assert any(s.actor == "defense" for s in flow)
