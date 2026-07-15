# Adversarial Sandbox — Backend

## Setup
```bash
cd backend
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
pip install torchvision            # one-time, for the training script only
python scripts/train_mnist.py      # one-time, downloads MNIST, writes models/*.pt
```

## Test
```bash
pytest -v
```

## Run
```bash
uvicorn adversarial_sandbox.api:app --reload --port 8000
```

## API
- `GET  /attacks` — list modules
- `GET  /attacks/{id}` — lesson + knob schema
- `POST /attacks/{id}/run` — apply attack (JSON body = params)
- `POST /attacks/{id}/defend` — apply defense

## Adding an attack
Drop a file in `adversarial_sandbox/attacks/`, subclass `AttackModule`, decorate
with `@register_attack`, add an import line to `attacks/__init__.py`. The API and
contract test pick it up automatically.
