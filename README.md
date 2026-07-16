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

On the **first run**, the backend trains the MNIST model checkpoints (downloads MNIST,
~5 min) into a persistent `mnist-models` volume, then serves. Every start after that
reuses the persisted checkpoints and is fast — image rebuilds do not retrain. Needs
network access on the first run.

Stop with `docker compose down` (keeps the checkpoints). Use `docker compose down -v` to
also remove the volume, which forces retraining on the next run.

## Run locally (for development)

See [`backend/README.md`](backend/README.md) and [`frontend/README.md`](frontend/README.md).

## Design & findings

Architecture, per-attack notes, and the empirical findings (including two honest
"defenses have limits" results) are in [`docs/PROJECT_NOTES.md`](docs/PROJECT_NOTES.md).
