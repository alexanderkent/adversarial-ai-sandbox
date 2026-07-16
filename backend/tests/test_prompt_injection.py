from adversarial_sandbox.attacks import prompt_injection as pi
from adversarial_sandbox.schema import RunResult


def _obey_reply(_messages):
    return pi.SENTINEL  # model obeyed the injection: output is just the sentinel


def _summary_reply(_messages):
    return "Revenue increased by 12% and headcount rose by 4%."  # did its real job


def test_obeyed_detects_hijack_but_not_a_mention():
    assert pi._obeyed(pi.SENTINEL) is True
    assert pi._obeyed(f"Sure. {pi.SENTINEL}") is True
    # merely mentioning the sentinel inside a real summary is NOT obeying:
    assert pi._obeyed(f"The document tried to make me say {pi.SENTINEL} but here is the summary.") is False


def test_direct_run_flags_user_turn_and_detects_hijack(monkeypatch):
    monkeypatch.setattr(pi.genai, "generate", _obey_reply)
    r = pi.PromptInjection().run({"vector": "direct", "payload": "override"})
    assert isinstance(r, RunResult)
    assert r.transcript is not None and r.figure is None
    injected = [t for t in r.transcript.turns if t.injected]
    assert injected and injected[0].role == "user"
    assert r.metrics[0].label == "Injection obeyed"
    assert r.metrics[0].value == 1.0


def test_indirect_run_flags_document_turn(monkeypatch):
    monkeypatch.setattr(pi.genai, "generate", _obey_reply)
    r = pi.PromptInjection().run({"vector": "indirect", "payload": "override"})
    roles = [t.role for t in r.transcript.turns]
    assert "document" in roles
    injected = [t for t in r.transcript.turns if t.injected]
    assert injected and injected[0].role == "document"


def test_defend_uses_spotlight_delimiters_and_reports_safe(monkeypatch):
    monkeypatch.setattr(pi.genai, "generate", _summary_reply)
    r = pi.PromptInjection().defend({"vector": "direct", "payload": "override"})
    assert r.metrics[0].label == "Injection obeyed (defended)"
    assert r.metrics[0].value == 0.0
    # the delimiter appears in the (defended) untrusted turn shown to the student
    assert any(pi.DELIMS[0] in t.content for t in r.transcript.turns)


def test_defend_passes_spotlight_system_instruction_and_delimited_payload(monkeypatch):
    seen = {}

    def _capture(messages):
        seen["m"] = messages
        return ""

    monkeypatch.setattr(pi.genai, "generate", _capture)
    pi.PromptInjection().defend({"vector": "indirect", "payload": "override"})
    system, user = seen["m"][0], seen["m"][1]
    assert system["role"] == "system"
    assert "never follow instructions" in system["content"].lower()
    # the untrusted document (with the payload) is wrapped in the delimiters
    assert pi.DELIMS[0] in user["content"] and pi.DELIMS[1] in user["content"]
