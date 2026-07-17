<div align="center">

# 🧪 Adversarial AI Sandbox

**Break a model, then defend it — in your browser.**

An interactive teaching sandbox for adversarial machine learning. Pick an attack, read a
guided lesson (real math + the actual source code), tune the knobs, run it, and watch the
model fail — then flip on the paired defense and watch what it can (and *can't*) fix.

*Every attack ships with its defense — because attacks are only half the story.*

![MIT License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/backend-FastAPI%20%2B%20PyTorch-3776AB)
![TypeScript](https://img.shields.io/badge/frontend-React%20%2B%20Vite-3178C6)
![Attacks](https://img.shields.io/badge/attacks-6-8A2BE2)
![MITRE ATLAS](https://img.shields.io/badge/mapped%20to-MITRE%20ATLAS-red)

<img src="docs/img/hero.png" alt="Adversarial AI Sandbox — Backdoor lesson with a live result" width="880">

</div>

## Why this exists

Adversarial ML is usually taught as slides and equations. This sandbox makes it *hands-on*:
you can see a one-pixel-budget perturbation flip a digit's label, a poisoned blob bend a
decision boundary, or a prompt-injection string get past a naive filter — and then try the
defense yourself. It's built to answer "okay, but does the defense actually work?" honestly —
**two of the defenses have deliberate, visible limits**, because in the real world they do too.

## The six attacks (each with a paired defense)

| Attack | What you do | Paired defense | MITRE ATLAS |
|---|---|---|---|
| **Data Poisoning** (2D sklearn) | Flip labels & inject a poison blob to bend the boundary | Super-majority label cleaning | [AML.T0020](https://atlas.mitre.org/techniques/AML.T0020) Poison Training Data |
| **Adversarial Perturbation** (FGSM/PGD, MNIST) | Add a tiny L∞ perturbation to fool the classifier | Adversarial training | [AML.T0015](https://atlas.mitre.org/techniques/AML.T0015) · [AML.T0043](https://atlas.mitre.org/techniques/AML.T0043) |
| **Carlini & Wagner** (targeted L2, MNIST) | Optimize a minimal perturbation to a *chosen* target class | Adversarial training | [AML.T0015](https://atlas.mitre.org/techniques/AML.T0015) · [AML.T0043](https://atlas.mitre.org/techniques/AML.T0043) |
| **Backdoor** (BadNets trigger, MNIST) | Plant a trigger→target rule at training time | Fine-pruning | [AML.T0018](https://atlas.mitre.org/techniques/AML.T0018) Manipulate AI Model |
| **Prompt Injection** (local Qwen2.5-1.5B) | Hijack a summarizer directly or via a poisoned RAG doc | Spotlighting / delimiting *(honestly partial)* | [AML.T0051](https://atlas.mitre.org/techniques/AML.T0051) LLM Prompt Injection |
| **Prompt-Injection Filter Evasion** (TF-IDF) | Slip an injection past a keyword filter — 7 techniques | Input normalization *(can't undo them all)* | [AML.T0015](https://atlas.mitre.org/techniques/AML.T0015) Evade AI Model |

Adding a new attack is **one backend module file with zero frontend changes** — the UI is
driven entirely by each attack's schema (its knobs, lesson, formula, code, and result type).

## Quickstart (Docker)

```bash
docker compose up --build
```

Then open **http://localhost:5173** (the API runs on http://localhost:8000).

On the **first run**, the backend downloads MNIST and trains the model checkpoints (~5 min)
into a persistent `mnist-models` volume, then serves. Every start after that reuses the
checkpoints and is fast — image rebuilds don't retrain. First run needs network access.

Stop with `docker compose down` (keeps the checkpoints); `docker compose down -v` also removes
the volume and forces a retrain next time.

Running locally for development: see [`backend/README.md`](backend/README.md) and
[`frontend/README.md`](frontend/README.md).

## What's in the UI

- **Lesson · Flow · Code · Sweep** tabs per attack — the guided explainer, an actor-color-coded
  step diagram, the real source snippets (highlighted), and a live parameter-sweep chart that
  overlays the defended curve on the attacked one.
- **MITRE ATLAS** coverage matrix — every attack mapped to its real-world technique and tactic.
- **Interactive decision-boundary explorer** for poisoning (pure-SVG, morph clean⇄poisoned⇄sanitized).
- **Light / dark** theme throughout.

## Tech

- **Backend:** FastAPI · scikit-learn · PyTorch · 🤗 transformers (a real, key-free local LLM) — `backend/`
- **Frontend:** React · TypeScript · Vite · Tailwind · KaTeX · highlight.js — `frontend/`
- **Tests:** 127 backend (pytest) · 65 frontend (vitest)

## Design & findings

Architecture, per-attack notes, and the empirical findings — including the two honest
"defenses have limits" results — are in [`docs/PROJECT_NOTES.md`](docs/PROJECT_NOTES.md).

## Homage

Built while studying adversarial AI at **Purdue (CNIT 573 / TECH 57300 — "Adversarial
Techniques in AI")**. This is a personal learning project, not affiliated with or endorsed by
the university or the course staff.

## License

[MIT](LICENSE) © 2026 Alexander Kent
