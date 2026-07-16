import json

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from . import attacks  # noqa: F401  (import registers all modules)
from .registry import list_attacks, get_attack
from .schema import AttackDescription, RunResult

app = FastAPI(title="Adversarial Sandbox API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/attacks")
def list_all():
    out = []
    for m in list_attacks():
        d = m.describe()
        out.append({"id": d.id, "name": d.name, "group": d.group, "summary": d.summary})
    return out


def _module_or_404(attack_id: str):
    try:
        return get_attack(attack_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Unknown attack {attack_id!r}")


@app.get("/attacks/{attack_id}", response_model=AttackDescription)
def describe(attack_id: str):
    return _module_or_404(attack_id).describe()


def _invoke(method_name: str, attack_id: str, params: dict) -> RunResult:
    module = _module_or_404(attack_id)
    try:
        return getattr(module, method_name)(params)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.post("/attacks/{attack_id}/run", response_model=RunResult)
def run(attack_id: str, params: dict = Body(default={})):
    return _invoke("run", attack_id, params)


@app.post("/attacks/{attack_id}/defend", response_model=RunResult)
def defend(attack_id: str, params: dict = Body(default={})):
    return _invoke("defend", attack_id, params)


@app.post("/attacks/{attack_id}/sweep")
def sweep(attack_id: str, params: dict = Body(default={})):
    module = _module_or_404(attack_id)
    if module.describe().sweep is None:
        raise HTTPException(status_code=404, detail=f"{attack_id!r} has no sweep")

    def gen():
        try:
            for point in module.sweep(params):
                yield json.dumps(point) + "\n"
        except ValueError as e:
            yield json.dumps({"error": str(e)}) + "\n"
        yield json.dumps({"done": True}) + "\n"

    return StreamingResponse(gen(), media_type="application/x-ndjson")
