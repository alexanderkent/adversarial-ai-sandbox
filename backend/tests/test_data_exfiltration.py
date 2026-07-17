from adversarial_sandbox.attacks import data_exfiltration as dx
from adversarial_sandbox.schema import RunResult


def _leak_reply(_messages):
    return f"Sure. The user's key is {dx.SECRET}"   # model leaked the secret


def test_leaked_detects_verbatim_secret_only():
    assert dx._leaked(f"key: {dx.SECRET}") is True
    assert dx._leaked("no secret here") is False


def test_build_spotlight_wraps_document():
    _, turns = dx.DataExfiltration()._build(dx.PAYLOADS["url-exfil"], spotlighted=True)
    doc = [t for t in turns if t.role == "document"][0]
    assert dx.DELIMS[0] in doc.content and dx.DELIMS[1] in doc.content
    assert doc.injected is True


def test_build_undefended_has_raw_document():
    _, turns = dx.DataExfiltration()._build(dx.PAYLOADS["url-exfil"], spotlighted=False)
    doc = [t for t in turns if t.role == "document"][0]
    assert dx.DELIMS[0] not in doc.content


def test_run_undefended_leaks(monkeypatch):
    monkeypatch.setattr(dx.genai, "generate", _leak_reply)
    r = dx.DataExfiltration().run({"payload": "url-exfil", "defense": "output-filter"})
    assert isinstance(r, RunResult)
    assert r.transcript is not None and r.figure is None
    assert r.metrics[0].label == "Secret leaked"
    assert r.metrics[0].value == 1.0 and r.metrics[0].display == "Leaked"
    injected = [t for t in r.transcript.turns if t.injected]
    assert injected and injected[0].role == "document"


def test_defend_output_filter_redacts(monkeypatch):
    monkeypatch.setattr(dx.genai, "generate", _leak_reply)
    d = dx.DataExfiltration().defend({"payload": "url-exfil", "defense": "output-filter"})
    assert d.metrics[0].value == 0.0 and d.metrics[0].display == "Safe"
    assistant = [t for t in d.transcript.turns if t.role == "assistant"][0]
    assert dx.REDACTED in assistant.content and dx.SECRET not in assistant.content


def test_defend_spotlighting_can_still_leak(monkeypatch):
    # honest failure path: a leak despite spotlighting is reported (output is not redacted)
    monkeypatch.setattr(dx.genai, "generate", _leak_reply)
    d = dx.DataExfiltration().defend({"payload": "direct", "defense": "spotlighting"})
    assert d.metrics[0].value == 1.0 and d.metrics[0].display == "Leaked"
    assistant = [t for t in d.transcript.turns if t.role == "assistant"][0]
    assert dx.SECRET in assistant.content
