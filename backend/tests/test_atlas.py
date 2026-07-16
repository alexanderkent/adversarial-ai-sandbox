import re
from adversarial_sandbox.atlas import technique, TACTICS, CONTEXT_TECHNIQUES
from adversarial_sandbox import attacks  # noqa: F401  (register modules)
from adversarial_sandbox.registry import list_attacks, get_attack


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


def test_every_module_maps_to_atlas():
    for m in list_attacks():
        d = m.describe()
        assert d.atlas, f"{d.id} has no ATLAS mapping"
        for t in d.atlas:
            assert re.match(r"^AML\.T\d+$", t.id), t.id
            assert t.tactic in TACTICS, f"{d.id}: {t.tactic!r} not a column"
            assert t.name


def test_specific_mappings():
    def ids(aid):
        return {t.id for t in get_attack(aid).describe().atlas}
    assert ids("poisoning") == {"AML.T0020"}
    assert ids("backdoor") == {"AML.T0018"}
    assert ids("perturbation") == {"AML.T0015", "AML.T0043"}
    assert ids("carlini_wagner") == {"AML.T0015", "AML.T0043"}
    assert ids("text_evasion") == {"AML.T0015"}
    assert ids("prompt_injection") == {"AML.T0051"}


def test_prompt_injection_has_subtechniques():
    t = get_attack("prompt_injection").describe().atlas[0]
    sub = {s.id for s in t.subtechniques}
    assert sub == {"AML.T0051.000", "AML.T0051.001"}
