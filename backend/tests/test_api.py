import json

from fastapi.testclient import TestClient
from adversarial_sandbox.api import app

client = TestClient(app)


def _read_ndjson(resp):
    return [json.loads(line) for line in resp.text.splitlines() if line.strip()]


def test_list_attacks_includes_both_modules():
    r = client.get("/attacks")
    assert r.status_code == 200
    ids = {a["id"] for a in r.json()}
    assert {"poisoning", "perturbation"} <= ids


def test_describe_unknown_is_404():
    assert client.get("/attacks/nope").status_code == 404


def test_run_poisoning_returns_decision_surface():
    r = client.post("/attacks/poisoning/run",
                    json={"dataset": "blobs", "flip_pct": 30, "n_poison": 10, "seed": 0})
    assert r.status_code == 200
    body = r.json()
    assert body["figure"] is None
    ds = body["decision_surface"]
    assert ds["kind"] == "decision_surface"
    assert len(ds["states"]) == 2
    assert len(body["metrics"]) == 2


def test_invalid_params_is_422():
    r = client.post("/attacks/poisoning/run", json={"flip_pct": 999})
    assert r.status_code == 422


def test_run_unknown_attack_is_404():
    r = client.post("/attacks/nope/run", json={})
    assert r.status_code == 404


def test_missing_checkpoint_is_503(monkeypatch):
    # a module whose checkpoint is missing surfaces as 503, not a 500 crash
    from adversarial_sandbox.adapters import mnist

    monkeypatch.setattr(mnist, "STANDARD_PATH", mnist.MODELS_DIR / "does_not_exist.pt")
    r = client.post(
        "/attacks/perturbation/run",
        json={"sample_index": 0, "epsilon": 0.1, "mode": "fgsm"},
    )
    assert r.status_code == 503


def test_sweep_poisoning_streams_points_and_done():
    r = client.post("/attacks/poisoning/sweep",
                    json={"dataset": "blobs", "seed": 0})
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/x-ndjson")
    lines = _read_ndjson(r)
    assert lines[-1] == {"done": True}
    points = [l for l in lines if "x" in l]
    assert len(points) == 5  # n_poison sweep has 5 x-values
    assert all("attacked" in p and "defended" in p for p in points)


def test_sweep_unknown_attack_is_404():
    assert client.post("/attacks/nope/sweep", json={}).status_code == 404


def test_sweep_module_without_spec_is_404(monkeypatch):
    from adversarial_sandbox.registry import get_attack
    mod = get_attack("poisoning")
    orig = type(mod).describe
    monkeypatch.setattr(type(mod), "describe",
                        lambda self: orig(self).model_copy(update={"sweep": None}))
    assert client.post("/attacks/poisoning/sweep", json={}).status_code == 404


def test_atlas_endpoint_returns_matrix():
    r = client.get("/atlas")
    assert r.status_code == 200
    body = r.json()
    tactics = [c["tactic"] for c in body["tactics"]]
    assert "Defense Evasion" in tactics
    cells = {cell["id"]: cell for col in body["tactics"] for cell in col["cells"]}
    assert cells["AML.T0051"]["covered"] is True
    assert {a["attack_id"] for a in cells["AML.T0051"]["attacks"]} == {"prompt_injection"}
