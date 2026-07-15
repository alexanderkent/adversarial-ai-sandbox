# Adversarial Sandbox

An interactive web sandbox for learning adversarial machine learning. Pick an attack,
read a guided lesson (with real math and the actual source code), tune its parameters,
run it, and watch the effect — then toggle the paired defense.

**Attacks:** data poisoning · FGSM/PGD evasion · Carlini & Wagner (targeted L2) ·
BadNets backdoor. Each ships with a paired defense and a schema-driven UI, so adding a
new attack is one backend module file with zero frontend changes.

- Backend: FastAPI + scikit-learn + PyTorch (`backend/`)
- Frontend: React + TypeScript + Vite + Tailwind, KaTeX + highlight.js (`frontend/`)

## Run with Docker (recommended)

```bash
docker compose up --build
```
Then open **http://localhost:5173** (the API is on http://localhost:8000).

The first build is slow (~5 min): the backend's builder stage downloads MNIST and trains
the model checkpoints, then copies them into a lean runtime image. Subsequent starts are
fast. Needs network access during the build.

Stop with `docker compose down`.

## Run locally (for development)

See [`backend/README.md`](backend/README.md) and [`frontend/README.md`](frontend/README.md).

## Design & findings

Architecture, per-attack notes, and the empirical findings (including two honest
"defenses have limits" results) are in [`docs/PROJECT_NOTES.md`](docs/PROJECT_NOTES.md).
