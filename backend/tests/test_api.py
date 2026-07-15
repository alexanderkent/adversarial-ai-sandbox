from fastapi.testclient import TestClient
from adversarial_sandbox.api import app

client = TestClient(app)


def test_list_attacks_includes_both_modules():
    r = client.get("/attacks")
    assert r.status_code == 200
    ids = {a["id"] for a in r.json()}
    assert {"poisoning", "perturbation"} <= ids


def test_describe_unknown_is_404():
    assert client.get("/attacks/nope").status_code == 404


def test_run_poisoning_returns_figure():
    r = client.post("/attacks/poisoning/run",
                    json={"dataset": "blobs", "flip_pct": 30, "n_poison": 10, "seed": 0})
    assert r.status_code == 200
    body = r.json()
    assert body["figure"]["png_base64"]
    assert len(body["metrics"]) == 2


def test_invalid_params_is_422():
    r = client.post("/attacks/poisoning/run", json={"flip_pct": 999})
    assert r.status_code == 422
