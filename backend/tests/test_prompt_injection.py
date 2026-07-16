from adversarial_sandbox.attacks import prompt_injection as pi
from adversarial_sandbox.schema import RunResult


def _leak_reply(_messages):
    return f"Sure! The recovery code is {pi.SECRET}."


def _refuse_reply(_messages):
    return "I'm sorry, I can't share the recovery code."


def test_direct_run_flags_user_turn_and_detects_leak(monkeypatch):
    monkeypatch.setattr(pi.genai, "generate", _leak_reply)
    r = pi.PromptInjection().run({"vector": "direct", "payload": "direct-override"})
    assert isinstance(r, RunResult)
    assert r.transcript is not None and r.figure is None
    injected = [t for t in r.transcript.turns if t.injected]
    assert injected and injected[0].role == "user"
    assert r.metrics[0].label == "Secret leaked"
    assert r.metrics[0].value == 1.0


def test_indirect_run_flags_document_turn(monkeypatch):
    monkeypatch.setattr(pi.genai, "generate", _leak_reply)
    r = pi.PromptInjection().run({"vector": "indirect", "payload": "direct-override"})
    roles = [t.role for t in r.transcript.turns]
    assert "document" in roles
    injected = [t for t in r.transcript.turns if t.injected]
    assert injected and injected[0].role == "document"


def test_defend_uses_spotlight_delimiters_and_reports_no_leak(monkeypatch):
    monkeypatch.setattr(pi.genai, "generate", _refuse_reply)
    r = pi.PromptInjection().defend({"vector": "direct", "payload": "direct-override"})
    assert r.metrics[0].label == "Secret leaked (defended)"
    assert r.metrics[0].value == 0.0
    # the delimiter appears in the (defended) untrusted turn shown to the student
    assert any(pi.DELIMS[0] in t.content for t in r.transcript.turns)


def test_defend_passes_spotlight_system_instruction_to_model(monkeypatch):
    seen = {}
    monkeypatch.setattr(pi.genai, "generate",
                        lambda messages: seen.setdefault("m", messages) and "" or "")
    pi.PromptInjection().defend({"vector": "indirect", "payload": "authority"})
    system = seen["m"][0]
    assert system["role"] == "system"
    assert "never as instructions" in system["content"].lower()
