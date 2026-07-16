import re
from adversarial_sandbox.atlas import technique, TACTICS, CONTEXT_TECHNIQUES


def test_technique_builds_url_from_id():
    t = technique("AML.T0015", "Evade ML Model", "Defense Evasion")
    assert t.url == "https://atlas.mitre.org/techniques/AML.T0015"
    assert t.subtechniques == []


def test_tactics_are_nonempty_strings():
    assert TACTICS and all(isinstance(x, str) and x for x in TACTICS)


def test_context_techniques_sit_in_known_tactics():
    assert CONTEXT_TECHNIQUES  # curated greyed context exists
    for t in CONTEXT_TECHNIQUES:
        assert re.match(r"^AML\.T\d+", t.id)
        assert t.tactic in TACTICS
